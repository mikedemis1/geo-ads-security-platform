from fastapi import Header, HTTPException
from typing import Iterable
from .jwt_service import decode_and_verify, require_scopes, AuthError


def require_scope(required: Iterable[str]):
    async def _dep(authorization: str = Header(default=None)):
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Missing Bearer token")

        token = authorization.split()[1]

        try:
            payload = decode_and_verify(token)
            require_scopes(payload, required)
            return payload
        except AuthError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

    return _dep