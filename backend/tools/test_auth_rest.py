import requests, sys

BASE   = "http://127.0.0.1:8000"
SECRET = "CHANGE_ME_32BYTES_DEV_ONLY_000000"

print("=" * 55)
print("GEO-ADS — JWT REST Auth Acceptance Test")
print("=" * 55)

r = requests.post(
    f"{BASE}/auth/token",
    json={"sub": "test-runner", "scopes": ["ads:read", "placements:read", "recommendation:read", "layout:read"]},
    headers={"X-Admin-Secret": SECRET},
)
assert r.status_code == 200, f"[FAIL] /auth/token → {r.status_code}"
tok = r.json()["access_token"]
print(f"[PASS] /auth/token          → 200  (token length: {len(tok)})")

auth = {"Authorization": f"Bearer {tok}"}

r = requests.get(f"{BASE}/layout", headers=auth)
assert r.status_code == 200, f"[FAIL] GET /layout with token → {r.status_code}"
print(f"[PASS] GET /layout + Bearer → 200")

r = requests.get(f"{BASE}/layout")
assert r.status_code == 401, f"[FAIL] GET /layout no token → {r.status_code} (expected 401)"
print(f"[PASS] GET /layout no token → 401")

r = requests.get(f"{BASE}/layout/query/near?x=1&y=1&radius=2&zone_id=glassfloor", headers=auth)
assert r.status_code == 200, f"[FAIL] /layout/query/near → {r.status_code}"
print(f"[PASS] /layout/query/near   → 200")

r = requests.get(f"{BASE}/layout/multiindex", headers=auth)
assert r.status_code == 200, f"[FAIL] /layout/multiindex → {r.status_code}"
print(f"[PASS] /layout/multiindex   → 200")

sys.path.insert(0, ".")
from app.security.auth_config import JWT_SECRET
assert len(JWT_SECRET.encode()) >= 32, f"[FAIL] JWT_SECRET only {len(JWT_SECRET.encode())} bytes"
print(f"[PASS] JWT_SECRET length    → {len(JWT_SECRET.encode())} bytes (>= 32)")

print("=" * 55)
print("ALL 6 TESTS PASSED")
print("=" * 55)
