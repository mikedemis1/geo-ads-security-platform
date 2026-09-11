# backend/app/security/auth_routes.py
import logging

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from .jwt_service import mint_token, mint_refresh_token, decode_and_verify, require_token_type, AuthError
from .auth_config import ADMIN_TOKEN_SECRET, ADMIN_USER, ADMIN_PASS

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenReq(BaseModel):
    sub: str = "tech"
    scopes: list[str]


class LoginReq(BaseModel):
    username: str
    password: str


class RefreshReq(BaseModel):
    refresh_token: str


DEFAULT_SCOPES = [
    "ads:read", "placements:read", "recommendation:read",
    "layout:read", "placements:write", "security:read",
]


@router.post("/token")
@limiter.limit("5/minute")
async def issue_token(
    request: Request,
    body: TokenReq,
    x_admin_secret: str = Header(default=None),
):
    if x_admin_secret != ADMIN_TOKEN_SECRET:
        # Record threat event
        _record_auth_event(request, "auth_failed", body.sub)
        raise HTTPException(status_code=401, detail="Unauthorized")
    _record_auth_event(request, "auth_success", body.sub)
    return {"access_token": mint_token(body.sub, body.scopes)}


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, body: LoginReq):
    if body.username != ADMIN_USER or body.password != ADMIN_PASS:
        _record_auth_event(request, "auth_failed", body.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    _record_auth_event(request, "auth_success", body.username)
    return {
        "access_token": mint_token(body.username, DEFAULT_SCOPES),
        "refresh_token": mint_refresh_token(body.username, DEFAULT_SCOPES),
        "token_type": "bearer",  # nosec B105 - OAuth2 token type, not a password
        "expires_in": 3600,
    }


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh_token(request: Request, body: RefreshReq):
    """
    Exchange a refresh token for a new access token.
    Accepts refresh_token, returns a new access_token.
    """
    try:
        payload = decode_and_verify(body.refresh_token)
    except AuthError:
        _record_auth_event(request, "auth_failed", "refresh_attempt")
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    try:
        require_token_type(payload, "refresh")
    except AuthError:
        _record_auth_event(request, "auth_failed", "invalid_token_type")
        raise HTTPException(status_code=401, detail="Not a refresh token")

    sub = payload.get("sub", "unknown")
    scopes = (payload.get("scope") or "").split()

    _record_auth_event(request, "auth_success", sub)
    return {
        "access_token": mint_token(sub, scopes),
        "token_type": "bearer",  # nosec B105 - OAuth2 token type, not a password
        "expires_in": 3600,
    }


def _record_auth_event(request: Request, event_type: str, username: str) -> None:
    """Record auth events to the threat engine (if available)."""
    try:
        from app.security.threat_engine import get_threat_engine
        engine = get_threat_engine()
        ip = request.client.host if request.client else "unknown"
        engine.record_event(
            event_type=event_type,
            source_ip=ip,
            details={"username": username, "path": str(request.url.path)},
        )
    except Exception as exc:  # detection must never block authentication
        logging.getLogger("app").warning("threat engine unavailable, auth event dropped: %s", exc)
