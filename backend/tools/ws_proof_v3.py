"""
WS Proof v3 — Anti-replay Window (Milestone v7)

Τρέχει 3 tests:
  1. Φρέσκο signed message → PASS (γίνεται δεκτό)
  2. Replay ίδιου message (ίδιο nonce) → REJECT (duplicate nonce)
  3. Παλιό timestamp (>60s) → REJECT (message too old)
"""

import asyncio
import json
import time
from datetime import datetime, timezone, timedelta

import websockets

# Χρησιμοποιούμε τα ίδια modules του project
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.security.jwt_service import mint_token
from app.security.message_schema import SignedMessage, NodeRole
from app.security.auth_config import ADMIN_TOKEN_SECRET

WS_URL = "ws://localhost:8000/ws/recommendation"
DIVIDER = "=" * 60


def _make_fresh_message() -> SignedMessage:
    """Φτιάχνει ένα σωστό signed message με fresh timestamp + unique nonce."""
    return SignedMessage.create(
        node_id="proof-v3",
        role=NodeRole.CONTROLLER,
        msg_type="RECOMMEND",
        payload={"x": 2.0, "y": 3.0, "radius": 10.0},
        secret_key=ADMIN_TOKEN_SECRET,
    )


def _make_old_message() -> SignedMessage:
    """Φτιάχνει signed message με timestamp 120 δευτερόλεπτα στο παρελθόν."""
    msg = SignedMessage.create(
        node_id="proof-v3-old",
        role=NodeRole.CONTROLLER,
        msg_type="RECOMMEND",
        payload={"x": 2.0, "y": 3.0, "radius": 10.0},
        secret_key=ADMIN_TOKEN_SECRET,
    )
    # Αλλάζουμε το timestamp σε παλιό και ξανα-υπολογίζουμε HMAC
    msg.header.timestamp = datetime.now(timezone.utc) - timedelta(seconds=120)
    msg.compute_hmac(secret_key=ADMIN_TOKEN_SECRET)
    return msg


async def main():
    token = mint_token("proof-v3", ["recommendation:read"])

    print(DIVIDER)
    print("WS Proof v3 — Anti-replay Window (Milestone v7)")
    print(DIVIDER)

    # ── Test 1: Φρέσκο message → PASS ──
    print("\n[Test 1] Φρέσκο signed message...")
    async with websockets.connect(f"{WS_URL}?token={token}") as ws:
        msg = _make_fresh_message()
        await ws.send(msg.model_dump_json())
        resp = json.loads(await ws.recv())
        if "error" not in resp and "data" in resp:
            sid = resp["data"]["screen_id"]
            print(f"   PASS — Recommendation: screen_id={sid}")
        else:
            print(f"   FAIL — Unexpected: {resp}")

    # ── Test 2: Replay ίδιου message (ίδιο nonce) → REJECT ──
    print("\n[Test 2] Replay ίδιου message (ίδιο nonce)...")
    async with websockets.connect(f"{WS_URL}?token={token}") as ws:
        msg = _make_fresh_message()
        raw = msg.model_dump_json()

        # Στέλνουμε πρώτη φορά (πρέπει να γίνει δεκτό)
        await ws.send(raw)
        resp1 = json.loads(await ws.recv())

        # Στέλνουμε ΞΑΝΑ το ίδιο (ίδιο nonce → replay)
        await ws.send(raw)
        resp2 = json.loads(await ws.recv())

        if "error" in resp2 and "nonce" in resp2["error"].lower():
            print(f"   PASS — Απορρίφθηκε: {resp2['error']}")
        else:
            print(f"   FAIL — Unexpected: {resp2}")

    # ── Test 3: Παλιό timestamp (>60s) → REJECT ──
    print("\n[Test 3] Παλιό timestamp (120s στο παρελθόν)...")
    async with websockets.connect(f"{WS_URL}?token={token}") as ws:
        msg = _make_old_message()
        await ws.send(msg.model_dump_json())
        resp = json.loads(await ws.recv())
        if "error" in resp and "old" in resp["error"].lower():
            print(f"   PASS — Απορρίφθηκε: {resp['error']}")
        else:
            print(f"   FAIL — Unexpected: {resp}")

    print(f"\n{DIVIDER}")


if __name__ == "__main__":
    asyncio.run(main())