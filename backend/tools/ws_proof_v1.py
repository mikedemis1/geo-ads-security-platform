# tools/ws_proof_v1.py
# Milestone v1 — Αποδεικνύει ότι τα WebSocket endpoints απαιτούν JWT tokens
#
# Scenarios:
# Test 1: Χωρίς token        → WS close code 4401
# Test 2: Λάθος scope        → WS close code 4403
# Test 3: Σωστό token        → Σύνδεση επιτυχής

import asyncio
import json
import sys
sys.path.insert(0, ".")

import websockets

from app.security.jwt_service import mint_token

WS_PLACEMENTS = "ws://localhost:8000/ws/placements"
WS_ADS        = "ws://localhost:8000/ws/ads"


async def test_no_token():
    """Test 1: Χωρίς token — πρέπει να κλείσει με 4401"""
    print("\n[Test 1] Χωρίς token...")
    try:
        ws = await websockets.connect(WS_PLACEMENTS)
        await ws.recv()
        await ws.wait_closed()
        code = ws.close_code
        if code == 4401:
            print(f"  PASS — Έκλεισε με κωδικό {code} (Unauthorized)")
        else:
            print(f"  FAIL — Αναμενόταν 4401, πήραμε {code}")
    except websockets.exceptions.ConnectionClosedError as e:
        if e.code == 4401:
            print(f"  PASS — Έκλεισε με κωδικό {e.code} (Unauthorized)")
        else:
            print(f"  FAIL — Αναμενόταν 4401, πήραμε {e.code}")
    except Exception as e:
        print(f"  FAIL — {type(e).__name__}: {e}")


async def test_wrong_scope():
    """Test 2: Token με λάθος scope — πρέπει να κλείσει με 4403"""
    print("\n[Test 2] Token με λάθος scope (ads:read αντί placements:read)...")
    token = mint_token("test-user", ["ads:read"])  # λάθος scope για /ws/placements
    url = f"{WS_PLACEMENTS}?token={token}"
    try:
        ws = await websockets.connect(url)
        await ws.recv()
        await ws.wait_closed()
        code = ws.close_code
        if code == 4403:
            print(f"  PASS — Έκλεισε με κωδικό {code} (Forbidden)")
        else:
            print(f"  FAIL — Αναμενόταν 4403, πήραμε {code}")
    except websockets.exceptions.ConnectionClosedError as e:
        if e.code == 4403:
            print(f"  PASS — Έκλεισε με κωδικό {e.code} (Forbidden)")
        else:
            print(f"  FAIL — Αναμενόταν 4403, πήραμε {e.code}")
    except Exception as e:
        print(f"  FAIL — {type(e).__name__}: {e}")


async def test_correct_token():
    """Test 3: Σωστό token — πρέπει να συνδεθεί και να πάρει snapshot"""
    print("\n[Test 3] Σωστό token με placements:read scope...")
    token = mint_token("test-user", ["placements:read"])
    url = f"{WS_PLACEMENTS}?token={token}"
    try:
        ws = await websockets.connect(url)
        resp = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(resp)
        await ws.close()
        if data.get("type") == "placements_snapshot":
            print(f"  PASS — Συνδέθηκε και πήρε snapshot (placements: {len(data.get('data', []))})")
        else:
            print(f"  FAIL — Unexpected response: {data}")
    except Exception as e:
        print(f"  FAIL — {type(e).__name__}: {e}")


async def main():
    print("=" * 55)
    print("WS Proof v1 - JWT WebSocket Authentication")
    print("=" * 55)
    try:
        await asyncio.gather(test_no_token(), test_wrong_scope(), test_correct_token())
    except OSError as e:
        print(f"\nFAIL Connection error: {e}")
        print("Σιγουρεψου οτι ο server τρεχει: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\nFAIL Unexpected: {type(e).__name__}: {e}")
    print("\n" + "=" * 55)


if __name__ == "__main__":
    asyncio.run(main())