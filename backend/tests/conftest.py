"""Shared test setup.

The app reads its secrets from the environment at import time and refuses to
start without them, so the values below are set before anything under `app`
is imported. They are test-only values; the real ones live in backend/.env,
which is never read here because os.environ already has these keys set and
python-dotenv does not override existing variables.

Three pieces of state survive between requests and would leak between tests
if left alone: the threat engine singleton, the slowapi rate-limit counters
and the WebSocket nonce store. The autouse fixture resets all three.
"""

import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("JWT_SECRET", "test-only-jwt-secret-with-at-least-32-bytes")
os.environ.setdefault("ADMIN_TOKEN_SECRET", "test-only-admin-secret-with-32-bytes-ok")
os.environ.setdefault("ADMIN_USER", "admin")
os.environ.setdefault("ADMIN_PASS", "test-only-password")
os.environ.setdefault("DB_PASSWORD", "test-only-db-password")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(autouse=True)
def reset_shared_state():
    """Give every test a clean threat engine, rate limiter and nonce store."""
    import app.security.threat_engine as threat_engine_module
    from app.security.auth_routes import limiter
    import app.websockets.websockets as ws_module

    threat_engine_module._ENGINE = None
    limiter.reset()
    ws_module._seen_nonces.clear()
    yield
    threat_engine_module._ENGINE = None
    limiter.reset()
    ws_module._seen_nonces.clear()


@pytest.fixture(scope="session")
def client():
    from app.main import app

    return TestClient(app)


@pytest.fixture
def make_token():
    """Mint an access token for the given scopes."""
    from app.security.jwt_service import mint_token

    def _make(scopes, sub="tester"):
        return mint_token(sub, scopes)

    return _make


@pytest.fixture
def threat_engine():
    from app.security.threat_engine import get_threat_engine

    return get_threat_engine()
