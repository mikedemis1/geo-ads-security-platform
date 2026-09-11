"""WebSocket security: JWT on the handshake, HMAC on every message, anti-replay."""

import json
import os
from datetime import datetime, timedelta, timezone

import pytest
from starlette.websockets import WebSocketDisconnect

from app.security.crypto_engine import CryptoEngine, CryptoMode
from app.security.message_schema import MessageHeader, NodeRole, SignedMessage

WS_SECRET = os.environ["ADMIN_TOKEN_SECRET"]
RECOMMENDATION_PAYLOAD = {"x": 2.0, "y": 2.0, "radius": 10.0}


def _signed(payload=None, secret=WS_SECRET, crypto=None):
    return SignedMessage.create(
        node_id="controller-test",
        role=NodeRole.CONTROLLER,
        msg_type="recommendation",
        payload=payload or dict(RECOMMENDATION_PAYLOAD),
        secret_key=secret,
        crypto=crypto,
    )


def _connect(client, token):
    return client.websocket_connect(f"/ws/recommendation?token={token}")


def test_connection_without_token_is_closed_with_4401(client, threat_engine):
    with pytest.raises(WebSocketDisconnect) as closed:
        with client.websocket_connect("/ws/recommendation") as ws:
            ws.receive_text()
    assert closed.value.code == 4401
    assert len(threat_engine.get_events(event_type="ws_auth_failed")) == 1


def test_connection_with_wrong_scope_is_closed_with_4403(client, make_token):
    with pytest.raises(WebSocketDisconnect) as closed:
        with _connect(client, make_token(["ads:read"])) as ws:
            ws.receive_text()
    assert closed.value.code == 4403


def test_connection_with_invalid_token_is_closed_with_4401(client):
    with pytest.raises(WebSocketDisconnect) as closed:
        with _connect(client, "not.a.jwt") as ws:
            ws.receive_text()
    assert closed.value.code == 4401


def test_valid_signed_message_gets_a_reply(client, make_token):
    with _connect(client, make_token(["recommendation:read"])) as ws:
        ws.send_text(_signed().model_dump_json())
        reply = ws.receive_json()
    assert reply.get("type") == "screen_recommendation" or reply.get("error") == "No suitable screen found"


def test_message_that_is_not_a_signed_message_is_rejected(client, make_token):
    with _connect(client, make_token(["recommendation:read"])) as ws:
        ws.send_text(json.dumps({"x": 1, "y": 1}))
        reply = ws.receive_json()
    assert "Expected SignedMessage" in reply["error"]


def test_tampered_payload_fails_hmac_and_is_recorded(client, make_token, threat_engine):
    message = json.loads(_signed().model_dump_json())
    message["payload"]["x"] = 99.0  # changed after signing
    with _connect(client, make_token(["recommendation:read"])) as ws:
        ws.send_text(json.dumps(message))
        reply = ws.receive_json()
    assert "Invalid HMAC signature" in reply["error"]
    assert len(threat_engine.get_events(event_type="hmac_failed")) == 1


def test_message_signed_with_the_wrong_secret_fails_hmac(client, make_token):
    raw = _signed(secret="attacker-secret").model_dump_json()
    with _connect(client, make_token(["recommendation:read"])) as ws:
        ws.send_text(raw)
        reply = ws.receive_json()
    assert "Invalid HMAC signature" in reply["error"]


def test_replayed_message_is_rejected_on_the_second_delivery(client, make_token, threat_engine):
    raw = _signed().model_dump_json()
    with _connect(client, make_token(["recommendation:read"])) as ws:
        ws.send_text(raw)
        first = ws.receive_json()
        ws.send_text(raw)
        second = ws.receive_json()
    assert "Duplicate nonce" not in first.get("error", "")
    assert "Duplicate nonce" in second["error"]
    assert len(threat_engine.get_events(event_type="replay_detected")) == 1


def test_message_older_than_the_replay_window_is_rejected(client, make_token):
    header = MessageHeader(
        node_id="controller-test",
        role=NodeRole.CONTROLLER,
        msg_type="recommendation",
        timestamp=datetime.now(timezone.utc) - timedelta(seconds=120),
        nonce="old-message-nonce",
        alg="HMAC_SHA256",
    )
    stale = SignedMessage(header=header, payload=dict(RECOMMENDATION_PAYLOAD), hmac="")
    stale.compute_hmac(secret_key=WS_SECRET)
    with _connect(client, make_token(["recommendation:read"])) as ws:
        ws.send_text(stale.model_dump_json())
        reply = ws.receive_json()
    assert "Message too old" in reply["error"]


def test_message_from_the_future_is_rejected(client, make_token):
    header = MessageHeader(
        node_id="controller-test",
        role=NodeRole.CONTROLLER,
        msg_type="recommendation",
        timestamp=datetime.now(timezone.utc) + timedelta(seconds=30),
        nonce="future-message-nonce",
        alg="HMAC_SHA256",
    )
    early = SignedMessage(header=header, payload=dict(RECOMMENDATION_PAYLOAD), hmac="")
    early.compute_hmac(secret_key=WS_SECRET)
    with _connect(client, make_token(["recommendation:read"])) as ws:
        ws.send_text(early.model_dump_json())
        reply = ws.receive_json()
    assert "in the future" in reply["error"]


def test_sha3_engine_signs_and_verifies():
    sha3 = CryptoEngine(CryptoMode.HMAC_SHA3_256)
    message = _signed(crypto=sha3)
    assert message.header.alg == "HMAC_SHA3_256"
    assert message.verify_hmac(WS_SECRET, crypto=sha3)


def test_signature_from_one_hash_family_does_not_verify_under_the_other():
    sha2 = CryptoEngine(CryptoMode.HMAC_SHA256)
    sha3 = CryptoEngine(CryptoMode.HMAC_SHA3_256)
    message = _signed(crypto=sha2)
    assert not message.verify_hmac(WS_SECRET, crypto=sha3)


def test_unknown_crypto_mode_is_refused():
    with pytest.raises(ValueError):
        CryptoEngine("HMAC_MD5")


def test_refresh_token_is_rejected_on_the_websocket(client):
    """The WebSocket handshake decodes tokens the same way the HTTP layer does,
    so the refresh-token bypass reached it too.

    The message is sent before receiving. A rejected socket raises on the
    receive; an accepted one would sit waiting for the client to speak first,
    and receiving straight away would deadlock the test rather than fail it.
    """
    login = client.post("/auth/login", json={"username": os.environ["ADMIN_USER"], "password": os.environ["ADMIN_PASS"]})
    refresh = login.json()["refresh_token"]
    with pytest.raises(WebSocketDisconnect) as closed:
        with _connect(client, refresh) as ws:
            ws.send_text(_signed().model_dump_json())
            ws.receive_json()
    assert closed.value.code == 4401
