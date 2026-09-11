import time
from typing import Iterable, Dict, Any
import jwt
from .auth_config import JWT_SECRET, JWT_ALG, JWT_ISSUER, JWT_AUDIENCE, JWT_DEFAULT_TTL_SECONDS, REFRESH_TOKEN_TTL_SECONDS


class AuthError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def mint_token(sub: str, scopes: Iterable[str], ttl_seconds: int = JWT_DEFAULT_TTL_SECONDS) -> str:
    now = int(time.time())
    payload = {
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "sub": sub,
        "iat": now,
        "nbf": now,
        "exp": now + ttl_seconds,
        "scope": " ".join(sorted(set(scopes))),
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def mint_refresh_token(sub: str, scopes: Iterable[str]) -> str:
    now = int(time.time())
    payload = {
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "sub": sub,
        "iat": now,
        "nbf": now,
        "exp": now + REFRESH_TOKEN_TTL_SECONDS,
        "scope": " ".join(sorted(set(scopes))),
        "type": "refresh",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_and_verify(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALG],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={"require": ["exp", "iat", "nbf", "sub", "iss", "aud"]},
        )
    except jwt.ExpiredSignatureError:
        raise AuthError(401, "Token expired")
    except jwt.InvalidTokenError:
        raise AuthError(401, "Invalid token")


def require_token_type(payload: Dict[str, Any], expected: str) -> None:
    """Reject a token issued for a different purpose.

    Access and refresh tokens are signed with the same key and carry the same
    scopes; the "type" claim is the only thing separating them. Nothing read it
    until an independent review on 2026-09-11 pointed out that a refresh token,
    valid for 24 hours, was therefore accepted anywhere an access token was.
    """
    if payload.get("type") != expected:
        raise AuthError(401, f"Expected {expected} token")


def require_scopes(payload: Dict[str, Any], required: Iterable[str]) -> None:
    token_scopes = set((payload.get("scope") or "").split())
    if not set(required).issubset(token_scopes):
        raise AuthError(403, "Forbidden: missing scope")
