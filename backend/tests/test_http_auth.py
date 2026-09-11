"""HTTP-side security: bearer auth, scopes, rate limiting, security headers.

These go through the real FastAPI app. None of the routes used here touch
PostgreSQL, so the suite runs without a database.
"""

import os

PROTECTED = "/placements"  # needs placements:read, served from memory
ADMIN_SECRET = os.environ["ADMIN_TOKEN_SECRET"]


def test_missing_authorization_header_returns_401(client):
    response = client.get(PROTECTED)
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing Bearer token"


def test_non_bearer_authorization_header_returns_401(client):
    response = client.get(PROTECTED, headers={"Authorization": "Basic abc"})
    assert response.status_code == 401


def test_garbage_bearer_token_returns_401(client):
    response = client.get(PROTECTED, headers={"Authorization": "Bearer not.a.jwt"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_token_without_the_needed_scope_returns_403(client, make_token):
    token = make_token(["ads:read"])
    response = client.get(PROTECTED, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "missing scope" in response.json()["detail"]


def test_token_with_the_needed_scope_reaches_the_handler(client, make_token):
    token = make_token(["placements:read"])
    response = client.get(PROTECTED, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_token_endpoint_rejects_wrong_admin_secret_and_records_it(client, threat_engine):
    response = client.post(
        "/auth/token",
        json={"sub": "tester", "scopes": ["ads:read"]},
        headers={"X-Admin-Secret": "wrong"},
    )
    assert response.status_code == 401
    failed = threat_engine.get_events(event_type="auth_failed")
    assert len(failed) == 1
    assert failed[0]["details"]["username"] == "tester"


def test_token_endpoint_issues_a_token_with_the_requested_scopes(client):
    response = client.post(
        "/auth/token",
        json={"sub": "tester", "scopes": ["security:read"]},
        headers={"X-Admin-Secret": ADMIN_SECRET},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    ok = client.get("/security/alerts", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200


def test_login_with_wrong_password_returns_401(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "nope"})
    assert response.status_code == 401


def test_refresh_endpoint_refuses_an_access_token(client, make_token):
    access = make_token(["ads:read"])
    response = client.post("/auth/refresh", json={"refresh_token": access})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not a refresh token"


def test_refresh_endpoint_issues_a_new_access_token(client):
    login = client.post("/auth/login", json={"username": "admin", "password": os.environ["ADMIN_PASS"]})
    assert login.status_code == 200
    refresh = login.json()["refresh_token"]
    response = client.post("/auth/refresh", json={"refresh_token": refresh})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_sixth_token_request_in_a_minute_is_rate_limited_and_recorded(client, threat_engine):
    body = {"sub": "tester", "scopes": ["ads:read"]}
    headers = {"X-Admin-Secret": ADMIN_SECRET}
    statuses = [client.post("/auth/token", json=body, headers=headers).status_code for _ in range(6)]
    assert statuses[:5] == [200] * 5
    assert statuses[5] == 429
    limited = threat_engine.get_events(event_type="rate_limited")
    assert len(limited) == 1
    assert limited[0]["details"]["path"] == "/auth/token"


def test_every_response_carries_the_security_headers(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert "X-XSS-Protection" in response.headers


def test_security_headers_are_present_on_error_responses_too(client):
    response = client.get(PROTECTED)
    assert response.status_code == 401
    assert response.headers["X-Frame-Options"] == "DENY"


def test_api_responses_are_not_cacheable(client):
    """Tokens and security data must not end up in a shared or browser cache.
    ZAP baseline 2026-09-11 flagged the root and 404 responses as storable."""
    for path in ("/", "/health", "/does-not-exist"):
        response = client.get(path)
        assert response.headers.get("Cache-Control") == "no-store", path


def test_zone_id_with_a_null_byte_is_rejected_before_reaching_the_database(client, make_token):
    """ZAP API scan 2026-09-11: zone_id=%00 on /layout/postgis/near reached
    psycopg2 and came back as a 500. Input validation belongs at the boundary,
    so a zone id that is not a plain identifier must be a 422."""
    token = make_token(["layout:read"])
    response = client.get(
        "/layout/postgis/near",
        params={"lat": 1.2, "lon": 1.2, "zone_id": "\x00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_refresh_token_is_rejected_on_a_normal_route(client):
    """A refresh token must not work as a bearer credential.

    Found by an independent review on 2026-09-11, not by this suite. Both token
    kinds are signed with the same key and carry the same scopes; only the
    "type" claim separates them, and nothing was reading it. A refresh token is
    valid for 24 hours against an access token's one hour, so accepting one here
    silently extends every session by a day.
    """
    login = client.post("/auth/login", json={"username": "admin", "password": os.environ["ADMIN_PASS"]})
    refresh = login.json()["refresh_token"]
    response = client.get(PROTECTED, headers={"Authorization": f"Bearer {refresh}"})
    assert response.status_code == 401


def test_access_token_is_rejected_on_the_refresh_route(client, make_token):
    """The same check in the other direction, which already worked."""
    access = make_token(["ads:read"])
    assert client.post("/auth/refresh", json={"refresh_token": access}).status_code == 401
