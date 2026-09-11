import os
import sys
from dotenv import load_dotenv

# Loads backend/.env (this file lives in backend/app/security/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


def _require_env(name: str) -> str:
    """Require an environment variable; fail at startup if it is missing."""
    val = os.getenv(name)
    if not val:
        print(
            f"[FATAL] Environment variable {name} is not set. "
            f"Create a backend/.env file with {name}=<value>.",
            file=sys.stderr,
        )
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


JWT_ISSUER   = os.getenv("JWT_ISSUER", "geo-ads")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "geo-ads-ui")
JWT_SECRET   = _require_env("JWT_SECRET")
JWT_ALG      = "HS256"

ADMIN_TOKEN_SECRET      = _require_env("ADMIN_TOKEN_SECRET")
JWT_DEFAULT_TTL_SECONDS = int(os.getenv("JWT_DEFAULT_TTL_SECONDS", "3600"))
REFRESH_TOKEN_TTL_SECONDS = int(os.getenv("REFRESH_TOKEN_TTL_SECONDS", "86400"))  # 24h
ADMIN_USER              = _require_env("ADMIN_USER")
ADMIN_PASS              = _require_env("ADMIN_PASS")

if len(JWT_SECRET.encode()) < 32:
    raise RuntimeError(
        f"JWT_SECRET is only {len(JWT_SECRET.encode())} bytes — must be >= 32. "
        "Set a strong JWT_SECRET in backend/.env before running."
    )
