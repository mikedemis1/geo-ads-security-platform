from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from .jwt_service import mint_token
from .auth_config import ADMIN_TOKEN_SECRET

router = APIRouter(prefix="/auth", tags=["auth"])

class TokenReq(BaseModel):
    sub: str = "tech"
    scopes: list[str]

@router.post("/token")
def issue_token(body: TokenReq, x_admin_secret: str = Header(default=None)):
    if x_admin_secret != ADMIN_TOKEN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"access_token": mint_token(body.sub, body.scopes)}
