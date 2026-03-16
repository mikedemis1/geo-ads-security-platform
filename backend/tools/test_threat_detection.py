#!/usr/bin/env python3
"""
test_threat_detection.py — Proof-of-Concept: Threat Detection System

Simulates attacks against the GEO-ADS backend and verifies
that the ThreatEngine detects them correctly.

Tests:
  1. Brute force login (>5 failed attempts in 5 min)
  2. Token refresh with valid/invalid tokens
  3. Security headers verification
  4. Security API endpoints (alerts, events, stats, comparison)
  5. Input validation (SQL injection attempt blocked)

Usage:
  cd backend
  .venv\\Scripts\\python.exe tools/test_threat_detection.py
"""

import requests
import time
import sys
import json

BASE = "http://127.0.0.1:8000"
ADMIN_SECRET = "CHANGE_ME_32BYTES_DEV_ONLY_000000"
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

passed = 0
failed = 0
skipped = 0


def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  {GREEN}PASS{RESET} {name}")
        passed += 1
    else:
        print(f"  {RED}FAIL{RESET} {name} -- {detail}")
        failed += 1


def skip(name, reason=""):
    global skipped
    print(f"  {YELLOW}SKIP{RESET} {name} -- {reason}")
    skipped += 1


def section(title):
    print(f"\n{BOLD}{CYAN}{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}{RESET}")


def get_token():
    """Get a valid JWT token via /auth/login."""
    r = requests.post(f"{BASE}/auth/login", json={
        "username": "admin",
        "password": "geo2025",
    })
    data = r.json()
    return data.get("access_token"), data.get("refresh_token")


def main():
    global passed, failed

    print(f"\n{BOLD}{'=' * 56}")
    print("  GEO-ADS THREAT DETECTION -- PROOF OF CONCEPT")
    print(f"{'=' * 56}{RESET}")

    # ── 0. Health check ───────────────────────────────
    section("0. Health Check")
    try:
        r = requests.get(f"{BASE}/health", timeout=3)
        test("Backend reachable", r.status_code == 200, f"status={r.status_code}")
    except Exception as e:
        print(f"  {RED}FATAL{RESET} Backend not running at {BASE}: {e}")
        sys.exit(1)

    # ── Admin token για verification (ανεξάρτητο από επίθεση) ────────────
    # Ο επιτιθέμενος δεν έχει admin secret. Αυτό το token χρησιμοποιείται
    # μόνο για να ελέγξουμε αν η άμυνα λειτούργησε, όχι για την επίθεση.
    r_admin = requests.post(
        f"{BASE}/auth/token",
        json={"sub": "test-runner", "scopes": [
            "ads:read", "placements:read", "recommendation:read",
            "layout:read", "placements:write", "security:read"
        ]},
        headers={"X-Admin-Secret": ADMIN_SECRET},
    )
    if r_admin.status_code == 429:
        print(f"  {YELLOW}RATE LIMITED{RESET} -- Το σύστημα μπλοκάρει ακόμα και τα admin requests.")
        print(f"  {YELLOW}Ξαναπροσπάθησε μετά από 1 λεπτό.{RESET}")
        sys.exit(0)
    elif r_admin.status_code != 200:
        print(f"  {RED}FATAL{RESET} Δεν ήταν δυνατή η απόκτηση admin token: {r_admin.status_code}")
        sys.exit(1)
    admin_token = r_admin.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # ── 1. Login & Token Refresh (επίθεση — τρέχει όσες φορές θέλουμε) ──
    section("1. Login & Token Refresh")

    r = requests.post(f"{BASE}/auth/login", json={"username": "admin", "password": "geo2025"})
    login_status = r.status_code

    if login_status == 429:
        print(f"  {YELLOW}INFO{RESET} Login rate-limited (429) -- αμυνα μπλοκαρει τον επιτιθεμενο")
        print(f"  {YELLOW}     Ο επιτιθέμενος δεν παίρνει token. Συνεχίζει το test με admin token.{RESET}")
        skip("Login success", "rate-limited (429) -- αμυνα ενεργη")
        skip("Access token returned", "rate-limited")
        skip("Refresh token returned", "rate-limited")
        skip("Token type present", "rate-limited")
        skip("Token refresh works", "rate-limited")
        skip("New access token returned", "rate-limited")
        refresh_token = None
    else:
        test("Login success", login_status == 200)
        data = r.json()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        test("Access token returned", access_token is not None)
        test("Refresh token returned", refresh_token is not None)
        test("Token type present", data.get("token_type") == "bearer")

        # Test refresh
        if refresh_token:
            r = requests.post(f"{BASE}/auth/refresh", json={"refresh_token": refresh_token})
            test("Token refresh works", r.status_code == 200, f"status={r.status_code}")
            new_data = r.json()
            test("New access token returned", new_data.get("access_token") is not None)

    # Test invalid refresh (παντα τρεχει -- δεν εξαρταται απο login)
    r = requests.post(f"{BASE}/auth/refresh", json={"refresh_token": "invalid.token.here"})
    test("Invalid refresh rejected", r.status_code == 401)

    # ── 2. Security Headers ───────────────────────────
    section("2. Security Headers")

    r = requests.get(f"{BASE}/health")
    test("X-Frame-Options: DENY", r.headers.get("x-frame-options") == "DENY",
         f"got: {r.headers.get('x-frame-options')}")
    test("X-Content-Type-Options: nosniff", r.headers.get("x-content-type-options") == "nosniff",
         f"got: {r.headers.get('x-content-type-options')}")
    test("X-XSS-Protection present", r.headers.get("x-xss-protection") is not None)
    test("Content-Security-Policy present", r.headers.get("content-security-policy") is not None)
    test("Referrer-Policy present", r.headers.get("referrer-policy") is not None)

    # ── 3. Input Validation ───────────────────────────
    section("3. Input Validation (SQL injection prevention)")

    r = requests.get(f"{BASE}/layout/postgis/near",
                     params={"lat": "0; DROP TABLE", "lon": "21.7", "radius_m": "50"},
                     headers=headers)
    test("SQL injection in lat rejected", r.status_code == 422,
         f"status={r.status_code}")

    r = requests.get(f"{BASE}/layout/postgis/near",
                     params={"lat": "999", "lon": "21.7", "radius_m": "50"},
                     headers=headers)
    test("lat=999 (out of range) rejected", r.status_code == 422,
         f"status={r.status_code}")

    r = requests.get(f"{BASE}/layout/postgis/near",
                     params={"lat": "38.24", "lon": "21.73", "radius_m": "-5"},
                     headers=headers)
    test("Negative radius rejected", r.status_code == 422,
         f"status={r.status_code}")

    # ── 4. Brute Force Simulation ─────────────────────
    section("4. Brute Force Simulation (6 rapid failed logins)")

    for i in range(6):
        requests.post(f"{BASE}/auth/login", json={
            "username": "admin",
            "password": f"wrong_pass_{i}",
        })
        time.sleep(0.1)

    print(f"  {YELLOW}Sent 6 failed login attempts...{RESET}")
    time.sleep(0.5)

    # Check if brute force alert was created
    r = requests.get(f"{BASE}/security/alerts", headers=headers)
    test("Security alerts endpoint works", r.status_code == 200)
    alerts = r.json() if r.status_code == 200 else []
    if not isinstance(alerts, list):
        alerts = []
    brute_force_alerts = [a for a in alerts if a.get("alert_type") == "brute_force"]
    test("Brute force alert detected", len(brute_force_alerts) > 0,
         f"alerts found: {len(brute_force_alerts)}")

    if brute_force_alerts:
        alert = brute_force_alerts[-1]
        test("Alert severity is critical", alert.get("severity") == "critical")
        test("Alert has detection_time_ms", alert.get("detection_time_ms") is not None)
        test("Alert detected_by = rule", alert.get("detected_by") == "rule")

    # ── 5. Security Events API ────────────────────────
    section("5. Security Events API")

    r = requests.get(f"{BASE}/security/events", headers=headers)
    test("Events endpoint works", r.status_code == 200)
    events = r.json()
    test("Events recorded", len(events) > 0, f"count={len(events)}")

    auth_failed_events = [e for e in events if e.get("event_type") == "auth_failed"]
    test("auth_failed events present", len(auth_failed_events) >= 6,
         f"count={len(auth_failed_events)}")

    # Filter by type
    r = requests.get(f"{BASE}/security/events?event_type=auth_failed", headers=headers)
    test("Event filtering works", r.status_code == 200)
    filtered = r.json()
    test("Filtered events are auth_failed", all(e["event_type"] == "auth_failed" for e in filtered))

    # ── 6. Security Stats API ─────────────────────────
    section("6. Security Stats")

    r = requests.get(f"{BASE}/security/stats", headers=headers)
    test("Stats endpoint works", r.status_code == 200)
    stats = r.json()
    test("Stats has event_counts", "event_counts" in stats)
    test("Stats has total_events", stats.get("total_events", 0) > 0)
    test("Stats has active_alerts", "active_alerts" in stats)

    print(f"\n  {YELLOW}Stats: {json.dumps(stats, indent=2)}{RESET}")

    # ── 7. Detection Comparison ───────────────────────
    section("7. Detection Comparison (Rule vs Statistical)")

    r = requests.get(f"{BASE}/security/comparison", headers=headers)
    test("Comparison endpoint works", r.status_code == 200)
    comp = r.json()
    test("Has rule_total_detections", "rule_total_detections" in comp)
    test("Has statistical_total_detections", "statistical_total_detections" in comp)
    test("Has total_events_analyzed", comp.get("total_events_analyzed", 0) > 0)
    test("Has avg detection times", "rule_avg_detection_ms" in comp)

    print(f"\n  {YELLOW}Comparison:{RESET}")
    print(f"    Rule-only detections:        {comp.get('rule_only_detections', 0)}")
    print(f"    Statistical-only detections: {comp.get('statistical_only_detections', 0)}")
    print(f"    Both detected:               {comp.get('both_detected', 0)}")
    print(f"    Neither:                      {comp.get('neither_detected', 0)}")
    print(f"    Rule avg time:               {comp.get('rule_avg_detection_ms', 0):.4f} ms")
    print(f"    Statistical avg time:        {comp.get('statistical_avg_detection_ms', 0):.4f} ms")
    print(f"    Total events analyzed:       {comp.get('total_events_analyzed', 0)}")

    # ── 8. Security scope check ──────────────────────
    section("8. Authorization Check")

    r = requests.get(f"{BASE}/security/alerts")
    test("No token -> 401", r.status_code == 401)

    # ── Summary ───────────────────────────────────────
    print(f"\n{BOLD}{'=' * 56}")
    total = passed + failed + skipped
    if failed == 0 and skipped == 0:
        print(f"  {GREEN}ALL {total} TESTS PASSED{RESET}")
    elif failed == 0:
        print(f"  {GREEN}{passed} passed{RESET}, {YELLOW}{skipped} skipped{RESET} (rate-limited), 0 failed  out of {total}")
    else:
        print(f"  {GREEN}{passed} passed{RESET}, {YELLOW}{skipped} skipped{RESET}, {RED}{failed} failed{RESET}  out of {total}")
    print(f"{'=' * 56}{RESET}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
