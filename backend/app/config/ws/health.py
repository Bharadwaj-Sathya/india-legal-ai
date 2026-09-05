import time
import threading
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Shared health st       ate (written by Celery worker, read by this API)
# This module is imported by both celery_app.py and uvicorn, so the state
# dict is shared when running in the same process.  For multiprocess setups
# swap this for Redis (see bottom of file).
# ---------------------------------------------------------------------------

_health_lock = threading.Lock()

_health_state: dict = {
    "ready": False,
    "started_at": None,        # ISO-8601 string set by worker_ready signal
    "last_heartbeat": None,    # Unix timestamp updated every 30 s
}

HEARTBEAT_TIMEOUT_SECONDS = 90  # 3 missed 30 s cycles


def set_ready(started_at: str) -> None:
    """Called by the Celery worker_ready signal."""
    with _health_lock:
        _health_state["ready"] = True
        _health_state["started_at"] = started_at


def clear_ready() -> None:
    """Called by the Celery worker_shutdown signal."""
    with _health_lock:
        _health_state["ready"] = False
        _health_state["last_heartbeat"] = None


def update_heartbeat() -> None:
    """Called by the Celery heartbeat loop every 30 s."""
    with _health_lock:
        _health_state["last_heartbeat"] = time.time()


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class LivenessResponse(BaseModel):
    status: str                          # "alive" | "unhealthy" | "starting"
    heartbeat_age_seconds: Optional[float] = None


class ReadinessResponse(BaseModel):
    status: str                          # "ready" | "not_ready"
    started_at: Optional[str] = None


class HealthResponse(BaseModel):
    status: str                          # "healthy" | "degraded" | "unhealthy"
    ready: bool
    started_at: Optional[str]
    last_heartbeat: Optional[str]        # ISO-8601 UTC
    heartbeat_age_seconds: Optional[float]
    checked_at: str                      # ISO-8601 UTC


@app.get(
    "/live",
    response_model=LivenessResponse,
    summary="Liveness probe",
    tags=["health"],
)
def liveness(response: Response) -> LivenessResponse:
    """
    Returns **200** when the worker heartbeat is recent.
    Returns **503** when the heartbeat is stale or not yet started.
    """
    with _health_lock:
        last_hb = _health_state["last_heartbeat"]

    if last_hb is None:
        response.status_code = 503
        return LivenessResponse(status="starting")

    age = round(time.time() - last_hb, 1)

    if age > HEARTBEAT_TIMEOUT_SECONDS:
        response.status_code = 503
        return LivenessResponse(status="unhealthy", heartbeat_age_seconds=age)

    return LivenessResponse(status="alive", heartbeat_age_seconds=age)


@app.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness probe",
    tags=["health"],
)
def readiness(response: Response) -> ReadinessResponse:
    """
    Returns **200** once the worker has fired its `worker_ready` signal.
    Returns **503** while the worker is still starting up or has shut down.
    """
    with _health_lock:
        ready = _health_state["ready"]
        started_at = _health_state["started_at"]

    if not ready:
        response.status_code = 503
        return ReadinessResponse(status="not_ready")

    return ReadinessResponse(status="ready", started_at=started_at)


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Full health summary",
    tags=["health"],
)
def health(response: Response) -> HealthResponse:
    """
    Combined status endpoint — useful for dashboards and monitoring tools.
    Returns **200** (healthy), **206** (degraded — alive but not ready), or **503** (unhealthy).
    """
    with _health_lock:
        ready = _health_state["ready"]
        started_at = _health_state["started_at"]
        last_hb = _health_state["last_heartbeat"]

    now = time.time()
    checked_at = datetime.now(timezone.utc).isoformat()

    heartbeat_age: Optional[float] = None
    last_hb_iso: Optional[str] = None

    if last_hb is not None:
        heartbeat_age = round(now - last_hb, 1)
        last_hb_iso = datetime.fromtimestamp(last_hb, tz=timezone.utc).isoformat()

    alive = last_hb is not None and heartbeat_age <= HEARTBEAT_TIMEOUT_SECONDS

    if alive and ready:
        status = "healthy"
        response.status_code = 200
    elif alive and not ready:
        status = "degraded"
        response.status_code = 206
    else:
        status = "unhealthy"
        response.status_code = 503

    return HealthResponse(
        status=status,
        ready=ready,
        started_at=started_at,
        last_heartbeat=last_hb_iso,
        heartbeat_age_seconds=heartbeat_age,
        checked_at=checked_at,
    )