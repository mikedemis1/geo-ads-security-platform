"""JWT minting and verification, tested without the web layer."""

import time

import jwt
import pytest

from app.security import auth_config
from app.security.jwt_service import (
    AuthError,
    decode_and_verify,
    mint_refresh_token,
    mint_token,
    require_scopes,
)


def _forge(payload_overrides=None, secret=None, alg=None):
    """Build a token that looks like ours but with something wrong in it."""
    now = int(time.time())
    payload = {
        "iss": auth_config.JWT_ISSUER,
        "aud": auth_config.JWT_AUDIENCE,
        "sub": "tester",
        "iat": now,
        "nbf": now,
        "exp": now + 60,
        "scope": "ads:read",
        "type": "access",
    }
    payload.update(payload_overrides or {})
    return jwt.encode(payload, secret or auth_config.JWT_SECRET, algorithm=alg or auth_config.JWT_ALG)


def test_minted_token_round_trips_sub_and_scopes():
    token = mint_token("alice", ["placements:write", "ads:read"])
    payload = decode_and_verify(token)
    assert payload["sub"] == "alice"
    assert payload["scope"] == "ads:read placements:write"
    assert payload["type"] == "access"


def test_refresh_token_is_marked_as_refresh():
    payload = decode_and_verify(mint_refresh_token("alice", ["ads:read"]))
    assert payload["type"] == "refresh"


def test_expired_token_is_rejected_with_401():
    token = _forge({"exp": int(time.time()) - 10})
    with pytest.raises(AuthError) as err:
        decode_and_verify(token)
    assert err.value.status_code == 401
    assert err.value.detail == "Token expired"


def test_token_signed_with_another_secret_is_rejected():
    token = _forge(secret="a-different-secret-that-is-also-32-bytes")
    with pytest.raises(AuthError) as err:
        decode_and_verify(token)
    assert err.value.status_code == 401


def test_wrong_audience_is_rejected():
    with pytest.raises(AuthError):
        decode_and_verify(_forge({"aud": "someone-else"}))


def test_wrong_issuer_is_rejected():
    with pytest.raises(AuthError):
        decode_and_verify(_forge({"iss": "someone-else"}))


def test_unsigned_token_is_rejected():
    """alg=none is the classic JWT bypass. PyJWT refuses it because we pin HS256."""
    payload = jwt.decode(_forge(), options={"verify_signature": False})
    token = jwt.encode(payload, key=None, algorithm="none")
    with pytest.raises(AuthError):
        decode_and_verify(token)


@pytest.mark.parametrize("missing", ["exp", "iat", "nbf", "sub", "iss", "aud"])
def test_token_missing_a_required_claim_is_rejected(missing):
    payload = jwt.decode(_forge(), options={"verify_signature": False})
    del payload[missing]
    token = jwt.encode(payload, auth_config.JWT_SECRET, algorithm=auth_config.JWT_ALG)
    with pytest.raises(AuthError):
        decode_and_verify(token)


def test_require_scopes_accepts_a_superset():
    payload = {"scope": "ads:read placements:read security:read"}
    require_scopes(payload, ["ads:read", "placements:read"])


def test_require_scopes_rejects_a_missing_scope_with_403():
    payload = {"scope": "ads:read"}
    with pytest.raises(AuthError) as err:
        require_scopes(payload, ["placements:write"])
    assert err.value.status_code == 403


def test_require_scopes_treats_absent_scope_claim_as_no_scopes():
    with pytest.raises(AuthError):
        require_scopes({}, ["ads:read"])
