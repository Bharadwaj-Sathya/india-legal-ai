"""
config/ws/manager.py

Reference implementation of the WebSocket connection manager.

THE MOST COMMON BUG: double-serialization.
If your manager does:
    await ws.send_text(json.dumps(json.dumps(data)))   ← WRONG
    await ws.send_json(data)  and also json.dumps      ← WRONG

The frontend receives a JSON string of a JSON string.
Your manager.send() must call json.dumps(data) exactly ONCE.
"""

import json
import asyncio
from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Maps client_id → active WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        # FIX: close any existing connection for this client before replacing it
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].close(code=1000)
            except Exception:
                pass
        self.active_connections[client_id] = websocket
        print(f"[WS] ✅ Client connected: {client_id}  "
              f"(total={len(self.active_connections)})")

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        print(f"[WS] ❌ Client disconnected: {client_id}  "
              f"(total={len(self.active_connections)})")

    async def send(self, client_id: str, data: dict):
        """
        Send a JSON payload to a specific client.

        FIX: use send_text(json.dumps(data)) — NOT send_json(data).
        FastAPI's send_json() calls json.dumps internally; if you also
        call json.dumps before passing to send_json you get double-encoding.
        Using send_text with a single json.dumps is explicit and safe.
        """
        ws = self.active_connections.get(client_id)
        if ws is None:
            print(f"[WS] send() — client '{client_id}' not connected, dropping message")
            return
        try:
            await ws.send_text(json.dumps(data))   # ← single serialization
        except Exception as e:
            print(f"[WS] send() error for '{client_id}': {e}")
            self.disconnect(client_id)

    async def broadcast(self, data: dict):
        """Send a JSON payload to ALL connected clients."""
        if not self.active_connections:
            return
        payload = json.dumps(data)
        results = await asyncio.gather(
            *[ws.send_text(payload) for ws in self.active_connections.values()],
            return_exceptions=True,
        )
        # Clean up any connections that errored during broadcast
        dead = [
            cid for cid, result in zip(list(self.active_connections), results)
            if isinstance(result, Exception)
        ]
        for cid in dead:
            print(f"[WS] broadcast() — removing dead connection: {cid}")
            self.disconnect(cid)


# Singleton — import this everywhere
manager = ConnectionManager()