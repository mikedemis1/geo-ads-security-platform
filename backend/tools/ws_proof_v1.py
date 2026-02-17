import asyncio
import sys
import websockets

BASE = "ws://127.0.0.1:8000"


async def try_connect(name: str, url: str):
    print(f"\n=== {name} ===")
    print(url)
    try:
        async with websockets.connect(url) as ws:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=2)
                print("CONNECTED OK, received:", msg[:200])
            except asyncio.TimeoutError:
                print("CONNECTED OK, no message within 2s (still OK)")
            return True
    except Exception as e:
        print("CONNECT FAILED:", repr(e))
        return False


async def main():
    if len(sys.argv) < 3:
        print("Usage: python ws_proof_v1.py <adsJwt> <placementsJwt>")
        sys.exit(1)

    ads_jwt = sys.argv[1]
    placements_jwt = sys.argv[2]

    await try_connect("WS-1 missing token (expect FAIL/4401)", f"{BASE}/ws/ads")
    await try_connect("WS-2 wrong scope (expect FAIL/4403)", f"{BASE}/ws/ads?token={placements_jwt}")
    await try_connect("WS-3 correct scope (expect OK)", f"{BASE}/ws/ads?token={ads_jwt}")


if __name__ == "__main__":
    asyncio.run(main())
