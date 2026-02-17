from fastapi import WebSocket
from typing import Iterable
from .jwt_service import decode_and_verify, require_scopes, AuthError

def get_token(ws: WebSocket) -> str | None:
    return ws.query_params.get("token")

async def ws_require(ws: WebSocket, scopes: Iterable[str]):
    token = get_token(ws)
    if not token:
        raise AuthError(401, "Missing token")
    payload = decode_and_verify(token)
    require_scopes(payload, scopes)
    return payload
