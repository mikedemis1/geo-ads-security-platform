# backend/app/config.py
#
# Database connection settings. Host, port, name and user have defaults that
# match docker-compose.yml. The password does not: a default password in code
# is a credential in the repository, so the app refuses to start without it.

import os
import sys

import psycopg2


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(
            f"[FATAL] Environment variable {name} is not set. "
            f"Add {name}=<value> to backend/.env before starting the app.",
            file=sys.stderr,
        )
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "geo_ads")
DB_USER = os.getenv("DB_USER", "geo_ads_user")
DB_PASSWORD = _require_env("DB_PASSWORD")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
