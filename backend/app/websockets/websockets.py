import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

from app.services.advertisement_service import AdvertisementService
from app.services.placement_service import PlacementService
from app.services.layout_service import get_screen_index

# Security (Milestone v1)
from app.security.jwt_service import decode_and_verify, require_scopes, require_token_type, AuthError

# Security (Milestone v2c)
from app.security.message_schema import SignedMessage
from app.security.auth_config import ADMIN_TOKEN_SECRET

router = APIRouter()

# ── Anti-replay store (Milestone v7) ────────────────────────
REPLAY_WINDOW_SEC = 60   # messages older than this are rejected
_NONCE_MAX_SIZE   = 5000  # cap on stored nonces (anti-flood)
_seen_nonces: dict[str, float] = {}  # nonce → timestamp (epoch)
_nonce_msg_count: int = 0            # counter that drives periodic cleanup


def _cleanup_old_nonces() -> None:
    """Drop nonces older than twice the replay window."""
    cutoff = time.time() - (REPLAY_WINDOW_SEC * 2)
    stale = [n for n, ts in _seen_nonces.items() if ts < cutoff]
    for n in stale:
        del _seen_nonces[n]


def _check_replay(msg: SignedMessage) -> Optional[str]:
    """
    Check the timestamp window and de-duplicate the nonce.
    Returns an error string on failure, None when the message is acceptable.
    """
    global _nonce_msg_count

    now = datetime.now(timezone.utc)
    msg_time = msg.header.timestamp

    # 1. Timestamp window check
    age_sec = (now - msg_time).total_seconds()
    if age_sec > REPLAY_WINDOW_SEC:
        return f"Message too old ({age_sec:.0f}s > {REPLAY_WINDOW_SEC}s). Rejected."
    if age_sec < -5:
        return "Message timestamp is in the future. Rejected."

    # 2. Size cap
    if len(_seen_nonces) >= _NONCE_MAX_SIZE:
        _cleanup_old_nonces()
        if len(_seen_nonces) >= _NONCE_MAX_SIZE:
            return "Nonce store full. Message rejected."

    # 3. Nonce dedup
    nonce = msg.header.nonce
    if nonce in _seen_nonces:
        return "Duplicate nonce. Replay attack detected. Rejected."

    _seen_nonces[nonce] = time.time()

    _nonce_msg_count += 1
    if _nonce_msg_count % 100 == 0:
        _cleanup_old_nonces()

    return None


# ── Threat Event Helper ────────────────────────────────

def _record_threat_event(event_type: str, source_ip: str = "unknown", details: dict | None = None) -> None:
    """Record a security event to the threat engine (best effort)."""
    try:
        from app.security.threat_engine import get_threat_engine
        engine = get_threat_engine()
        engine.record_event(event_type=event_type, source_ip=source_ip, details=details or {})
    except Exception as exc:  # detection must never break the socket
        logging.getLogger("app").warning("threat engine unavailable, event dropped: %s", exc)


def _get_ws_ip(ws: WebSocket) -> str:
    """Extract client IP from WebSocket."""
    try:
        return ws.client.host if ws.client else "unknown"
    except Exception:
        return "unknown"


# ── End Anti-replay ─────────────────────────────────────────


async def _handle_recommendation_payload(
    ws: WebSocket,
    index,
    payload: dict,
) -> None:
    """
    Shared handler for the recommendation logic.
    """
    ad_id = payload.get("ad_id")
    x = payload.get("x")
    y = payload.get("y")
    radius = payload.get("radius", 10.0)
    screen_type = payload.get("screen_type")
    ad_category = payload.get("ad_category")
    time_window = payload.get("time_window")

    if x is None or y is None:
        await ws.send_json({"error": "Missing x/y in payload"})
        return

    zone_id: Optional[str] = None
    if ad_id is not None:
        try:
            ad_id_int = int(ad_id)
        except (TypeError, ValueError):
            await ws.send_json({"error": "Invalid ad_id (must be integer)."})
            return

        try:
            ad = AdvertisementService.get_by_id(ad_id_int)
        except Exception as e:
            print(f"[WS][ERR] recommendation ad lookup failed ad_id={ad_id_int}: {e}")
            await ws.send_json({"error": "Advertisement lookup failed (DB/service error)."})
            return

        if ad is None:
            await ws.send_json({"error": "Advertisement not found"})
            return
        zone_id = ad.zone

    result = index.recommend_screen(
        x=float(x),
        y=float(y),
        radius=float(radius),
        zone_id=zone_id,
        screen_type=screen_type,
        ad_category=ad_category,
        time_window=time_window,
    )

    if result is None:
        await ws.send_json({"error": "No suitable screen found"})
        return

    key, distance = result
    await ws.send_json({
        "v": 1,
        "type": "screen_recommendation",
        "data": {
            "screen_id": key.screen_id,
            "zone_id": key.zone_id,
            "x": key.x,
            "y": key.y,
            "screen_type": key.screen_type,
            "ad_category": key.ad_category,
            "time_window": key.time_window,
            "distance": distance,
        },
    })


def _hash_payload(obj) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


async def _ws_require_scope(ws: WebSocket, scopes: list[str]) -> Optional[dict]:
    token = ws.query_params.get("token")
    if not token:
        await ws.accept()
        print(f"[SEC][WS] 4401 missing token path={ws.url.path}")
        _record_threat_event("ws_auth_failed", _get_ws_ip(ws), {"reason": "missing_token", "path": ws.url.path})
        await ws.close(code=4401)
        return None

    try:
        payload = decode_and_verify(token)
        require_token_type(payload, "access")
        require_scopes(payload, scopes)
        return payload
    except AuthError as e:
        code = 4403 if e.status_code == 403 else 4401
        await ws.accept()
        print(f"[SEC][WS] {code} auth fail path={ws.url.path} detail={e.detail}")
        _record_threat_event("ws_auth_failed", _get_ws_ip(ws), {"reason": e.detail, "path": ws.url.path})
        await ws.close(code=code)
        return None
    except Exception as e:
        await ws.accept()
        print(f"[SEC][WS] 4401 unexpected auth error path={ws.url.path} err={e}")
        _record_threat_event("ws_auth_failed", _get_ws_ip(ws), {"reason": str(e), "path": ws.url.path})
        await ws.close(code=4401)
        return None


class WSManager:
    def __init__(self) -> None:
        self.placements_clients: Set[WebSocket] = set()

    async def register_placements(self, ws: WebSocket) -> None:
        self.placements_clients.add(ws)
        print(f"[WS] placements client connected ({len(self.placements_clients)})")
        snapshot = jsonable_encoder(PlacementService.list_all())
        await ws.send_json({"v": 1, "type": "placements_snapshot", "data": snapshot})

    def unregister_placements(self, ws: WebSocket) -> None:
        self.placements_clients.discard(ws)
        print(f"[WS] placements client disconnected ({len(self.placements_clients)})")

    async def broadcast_placement_assigned(self, placement) -> None:
        payload = {"v": 1, "type": "placement_assigned", "data": jsonable_encoder(placement)}
        dead = []
        for ws in list(self.placements_clients):
            try:
                await ws.send_json(payload)
            except Exception as e:
                print(f"[WS] send FAILED: {e}")
                dead.append(ws)
        for ws in dead:
            self.unregister_placements(ws)


ws_manager = WSManager()


@router.websocket("/ws/ads")
async def websocket_ads(ws: WebSocket):
    auth = await _ws_require_scope(ws, ["ads:read"])
    if auth is None:
        return

    await ws.accept()
    print(f"[WS] ads client connected sub={auth.get('sub')}")

    last_hash = None
    try:
        while True:
            ads = AdvertisementService.get_all()
            payload = {"v": 1, "type": "ads_list", "data": [ad.model_dump() for ad in ads]}
            h = _hash_payload(payload)
            if h != last_hash:
                await ws.send_json(payload)
                last_hash = h
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return
    finally:
        print("[WS] ads client disconnected")


@router.websocket("/ws/placements")
async def websocket_placements(ws: WebSocket):
    auth = await _ws_require_scope(ws, ["placements:read"])
    if auth is None:
        return

    await ws.accept()
    print(f"[WS] placements client connected sub={auth.get('sub')}")

    await ws_manager.register_placements(ws)
    try:
        while True:
            await ws.receive()
    except WebSocketDisconnect:
        ws_manager.unregister_placements(ws)
    finally:
        print("[WS] placements client disconnected")


@router.websocket("/ws/recommendation")
async def websocket_recommendation(ws: WebSocket):
    auth = await _ws_require_scope(ws, ["recommendation:read"])
    if auth is None:
        return

    await ws.accept()
    print(f"[WS] recommendation client connected sub={auth.get('sub')}")

    index = get_screen_index()
    client_ip = _get_ws_ip(ws)

    try:
        while True:
            raw = await ws.receive_text()

            # --- HMAC Verification (Milestone v2c) ---
            try:
                msg = SignedMessage.model_validate_json(raw)
            except Exception:
                await ws.send_json({"error": "Invalid message format. Expected SignedMessage."})
                continue

            if not msg.verify_hmac(secret_key=ADMIN_TOKEN_SECRET):
                print(f"[SEC][WS] HMAC FAILED node={msg.header.node_id}")
                _record_threat_event("hmac_failed", client_ip, {"node_id": msg.header.node_id})
                await ws.send_json({"error": "Invalid HMAC signature. Message rejected."})
                continue

            print(f"[SEC][WS] HMAC OK node={msg.header.node_id} role={msg.header.role}")

            # --- Anti-replay check (Milestone v7) ---
            replay_error = _check_replay(msg)
            if replay_error:
                print(f"[SEC][WS] REPLAY REJECTED node={msg.header.node_id} nonce={msg.header.nonce}: {replay_error}")
                _record_threat_event("replay_detected", client_ip, {"node_id": msg.header.node_id, "nonce": msg.header.nonce})
                await ws.send_json({"error": replay_error})
                continue

            print(f"[SEC][WS] REPLAY OK nonce={msg.header.nonce}")

            await _handle_recommendation_payload(ws, index, msg.payload)

    except WebSocketDisconnect:
        return
    finally:
        print("[WS] recommendation client disconnected")


@router.websocket("/ws/recommendation-simple")
async def websocket_recommendation_simple(ws: WebSocket):
    """
    Simplified recommendation WebSocket for the React frontend.
    """
    auth = await _ws_require_scope(ws, ["recommendation:read"])
    if auth is None:
        return

    await ws.accept()
    print(f"[WS] recommendation-simple client connected sub={auth.get('sub')}")

    index = get_screen_index()

    try:
        while True:
            raw = await ws.receive_text()

            try:
                payload = json.loads(raw)
            except Exception:
                await ws.send_json({"error": "Invalid JSON"})
                continue

            await _handle_recommendation_payload(ws, index, payload)

    except WebSocketDisconnect:
        return
    finally:
        print("[WS] recommendation-simple client disconnected")


# ── /ws/security — Real-time security alert stream ────────

@router.websocket("/ws/security")
async def websocket_security(ws: WebSocket):
    """
    Real-time security alerts via WebSocket.
    JWT scope: security:read
    Pushes alerts as they are detected by the ThreatEngine.
    """
    auth = await _ws_require_scope(ws, ["security:read"])
    if auth is None:
        return

    await ws.accept()
    print(f"[WS] security client connected sub={auth.get('sub')}")

    from app.security.threat_engine import get_threat_engine
    engine = get_threat_engine()
    engine.register_ws_client(ws)

    try:
        # Send current alerts snapshot
        alerts = engine.get_alerts()
        await ws.send_json({"type": "security_snapshot", "data": alerts})

        # Keep connection alive
        while True:
            await ws.receive()
    except WebSocketDisconnect:
        pass
    finally:
        engine.unregister_ws_client(ws)
        print("[WS] security client disconnected")
