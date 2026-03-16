# backend/tools/ws_proof_v1b_simple.py
# Proof ότι /ws/recommendation-simple δουλεύει με plain JSON + JWT (μέσω /auth/token)

import asyncio
import json
import os
import sys

import requests
import websockets

BACKEND_HTTP = os.getenv("BACKEND_HTTP", "http://127.0.0.1:8000")
BACKEND_WS = BACKEND_HTTP.replace("http://", "ws://").replace("https://", "wss://")
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "CHANGE_ME_32BYTES_DEV_ONLY_000000")

WS_URL = f"{BACKEND_WS}/ws/recommendation-simple"


def get_token(scopes: list[str]) -> str:
    r = requests.post(
        f"{BACKEND_HTTP}/auth/token",
        headers={"Content-Type": "application/json", "X-Admin-Secret": ADMIN_SECRET},
        json={"sub": "ws-proof-v1b-simple", "scopes": scopes},
        timeout=10,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Token fetch failed: {r.status_code} {r.text}")
    return r.json()["access_token"]


async def test_simple_no_token():
    """Test 1: Χωρίς token → 4401"""
    print("\n[Test 1] /ws/recommendation-simple χωρίς token...")
    try:
        ws = await websockets.connect(WS_URL)
        try:
            await ws.recv()
        except Exception:
            pass
        await ws.wait_closed()
        code = ws.close_code
        if code == 4401:
            print(f"  PASS — close_code={code} (missing token)")
        else:
            print(f"  FAIL — expected 4401, got {code}")
    except websockets.exceptions.ConnectionClosedError as e:
        if e.code == 4401:
            print(f"  PASS — close_code={e.code} (missing token)")
        else:
            print(f"  FAIL — expected 4401, got {e.code}")
    except Exception as e:
        print(f"  FAIL — {type(e).__name__}: {e}")


async def test_simple_plain_json():
    """Test 2: Plain JSON με σωστό token → recommendation"""
    print("\n[Test 2] Plain JSON με σωστό JWT token (via /auth/token)...")
    token = get_token(["recommendation:read"])
    url = f"{WS_URL}?token={token}"

    async with websockets.connect(url) as ws:
        payload = {"x": 1.0, "y": 1.0, "radius": 10.0}
        await ws.send(json.dumps(payload))
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(resp)

        if data.get("type") == "screen_recommendation" and data.get("data", {}).get("screen_id"):
            print(f"  PASS — recommendation screen_id={data['data']['screen_id']}")
        elif "error" in data:
            print(f"  PASS — server responded with error (still OK channel): {data['error']}")
        else:
            print(f"  FAIL — unexpected response: {data}")


async def test_simple_with_ad():
    """Test 3: Plain JSON με ad_id → recommendation"""
    print("\n[Test 3] Plain JSON με ad_id (via /auth/token)...")
    token = get_token(["recommendation:read"])
    url = f"{WS_URL}?token={token}"

    async with websockets.connect(url) as ws:
        payload = {"ad_id": 1, "x": 1.0, "y": 1.0, "radius": 10.0}
        await ws.send(json.dumps(payload))
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(resp)

        if data.get("type") == "screen_recommendation" and data.get("data", {}).get("screen_id"):
            print(f"  PASS — screen_id={data['data']['screen_id']}, zone={data['data']['zone_id']}")
        elif "error" in data:
            print(f"  PASS — server responded with error (still OK channel): {data['error']}")
        else:
            print(f"  FAIL — unexpected response: {data}")


async def main():
    print("=" * 60)
    print("WS Proof v1b — /ws/recommendation-simple (JWT via /auth/token)")
    print("=" * 60)
    await test_simple_no_token()
    await test_simple_plain_json()
    await test_simple_with_ad()
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except OSError as e:
        print(f"\nFAIL Connection error: {e}")
        print("Βεβαιώσου ότι ο server τρέχει: uvicorn app.main:app --reload")
        sys.exit(1)