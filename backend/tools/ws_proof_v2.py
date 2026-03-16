# tools/ws_proof_v2.py
# Milestone v2c — HMAC Message Verification proof
# Compatible με websockets 16.0

import asyncio
import json
import sys
sys.path.insert(0, ".")

import websockets

from app.security.message_schema import SignedMessage, NodeRole
from app.security.auth_config import ADMIN_TOKEN_SECRET
from app.security.jwt_service import mint_token

WS_URL = "ws://localhost:8000/ws/recommendation"


def get_token():
    return mint_token("test-controller", ["recommendation:read"])


async def test_valid_hmac():
    print("\n[Test 1] Σωστό HMAC signed message...")
    token = get_token()
    url = f"{WS_URL}?token={token}"

    msg = SignedMessage.create(
        node_id="controller-1",
        role=NodeRole.CONTROLLER,
        msg_type="RECOMMENDATION_REQUEST",
        payload={"x": 5.0, "y": 5.0, "radius": 10.0},
        secret_key=ADMIN_TOKEN_SECRET,
    )

    ws = await websockets.connect(url)
    try:
        await ws.send(msg.model_dump_json())
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(resp)
        if data.get("type") == "screen_recommendation":
            print(f"  PASS — Recommendation: screen_id={data['data']['screen_id']}")
        elif "error" in data:
            print(f"  FAIL — Error: {data['error']}")
        else:
            print(f"  FAIL — Unexpected: {data}")
    finally:
        await ws.close()


async def test_invalid_hmac():
    print("\n[Test 2] Λάθος HMAC (tampered message)...")
    token = get_token()
    url = f"{WS_URL}?token={token}"

    msg = SignedMessage.create(
        node_id="attacker-1",
        role=NodeRole.CONTROLLER,
        msg_type="RECOMMENDATION_REQUEST",
        payload={"x": 5.0, "y": 5.0, "radius": 10.0},
        secret_key="WRONG_SECRET_KEY",
    )

    ws = await websockets.connect(url)
    try:
        await ws.send(msg.model_dump_json())
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(resp)
        if "error" in data and "HMAC" in data["error"]:
            print(f"  PASS — Απορρίφθηκε: {data['error']}")
        else:
            print(f"  FAIL — Επρεπε να απορριφθει: {data}")
    finally:
        await ws.close()


async def test_invalid_format():
    print("\n[Test 3] Plain JSON χωρίς υπογραφή...")
    token = get_token()
    url = f"{WS_URL}?token={token}"

    plain = json.dumps({"x": 5.0, "y": 5.0, "radius": 10.0})

    ws = await websockets.connect(url)
    try:
        await ws.send(plain)
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(resp)
        if "error" in data and "SignedMessage" in data["error"]:
            print(f"  PASS — Απορρίφθηκε: {data['error']}")
        else:
            print(f"  FAIL — Επρεπε να απορριφθει: {data}")
    finally:
        await ws.close()


async def main():
    print("=" * 55)
    print("WS Proof v2 - HMAC Message Verification")
    print("=" * 55)
    try:
        await test_valid_hmac()
        await test_invalid_hmac()
        await test_invalid_format()
    except OSError as e:
        print(f"\nFAIL Connection error: {e}")
        print("Σιγουρεψου οτι ο server τρεχει στο backend terminal")
    except Exception as e:
        print(f"\nFAIL Unexpected error: {type(e).__name__}: {e}")
    print("\n" + "=" * 55)


if __name__ == "__main__":
    asyncio.run(main())