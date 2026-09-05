import json
from config.ws.manager import manager
from src.features.gen_ai.llm import stream_llm_response


async def handle_ai_chat(client_id: str, data: dict):
    """
    Streams LLM tokens back to the client as they arrive.

    Client sends:
        { "type": "ai_chat", "message": "...", "conversation_id": "..." }

    Server pushes:
        { "type": "ai_start",  "conversation_id": "..." }
        { "type": "ai_token",  "token": "...", "conversation_id": "...", "done": false }
        { "type": "ai_token",  "token": "",    "conversation_id": "...", "done": true  }

    FIX: manager.send() must call websocket.send_text(json.dumps(data)) exactly ONCE.
    Double-serialization (json.dumps inside send AND again at the websocket layer)
    causes the frontend JSON.parse to receive a string-of-a-string, breaking rendering.
    """
    message = data.get("message", "").strip()
    # FIX: fall back to client_id so conversation_id is always a non-empty string
    conversation_id = data.get("conversation_id") or client_id
    system_prompt = data.get("system_prompt", "You are a helpful assistant.")

    if not message:
        await manager.send(client_id, {
            "type": "error",
            "detail": "Message cannot be empty.",
            "conversation_id": conversation_id,
        })
        return

    # Signal the frontend to create the assistant message bubble
    await manager.send(client_id, {
        "type": "ai_start",
        "conversation_id": conversation_id,
    })

    try:
        async for token in stream_llm_response(message, conversation_id, system_prompt):
            # FIX: only send non-empty tokens to avoid phantom whitespace in the bubble
            if token:
                await manager.send(client_id, {
                    "type": "ai_token",
                    "token": token,
                    "conversation_id": conversation_id,
                    "done": False,
                })

        # Signal end of stream — frontend sets isTyping=false on this
        await manager.send(client_id, {
            "type": "ai_token",
            "token": "",
            "conversation_id": conversation_id,
            "done": True,
        })

    except Exception as e:
        # FIX: always close the stream on error so the frontend doesn't hang in isTyping
        await manager.send(client_id, {
            "type": "error",
            "detail": str(e),
            "conversation_id": conversation_id,
        })


async def handle_ping(client_id: str, data: dict):
    await manager.send(client_id, {"type": "pong"})


# ── Server-pushed helpers (call from anywhere in your app) ────────────────────

async def push_notification(client_id: str, title: str, body: str):
    """Push a live notification to a specific connected client."""
    await manager.send(client_id, {
        "type": "notification",
        "title": title,
        "body": body,
    })


async def push_dashboard_update(metric: str, value):
    """Broadcast a dashboard metric update to ALL connected clients."""
    await manager.broadcast({
        "type": "dashboard_update",
        "metric": metric,
        "value": value,
    })