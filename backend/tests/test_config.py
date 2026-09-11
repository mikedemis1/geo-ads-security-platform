"""Configuration must refuse to start with a missing database password.

A default password in code is a credential in the repository. This test is
the guard against it coming back.
"""

import importlib

import pytest


def test_missing_db_password_stops_startup(monkeypatch):
    import app.config as config

    monkeypatch.delenv("DB_PASSWORD", raising=False)
    try:
        with pytest.raises(RuntimeError, match="DB_PASSWORD"):
            importlib.reload(config)
    finally:
        monkeypatch.undo()
        importlib.reload(config)


def test_jwt_secret_shorter_than_32_bytes_stops_startup(monkeypatch):
    import app.security.auth_config as auth_config

    monkeypatch.setenv("JWT_SECRET", "short")
    try:
        with pytest.raises(RuntimeError, match="JWT_SECRET"):
            importlib.reload(auth_config)
    finally:
        monkeypatch.undo()
        importlib.reload(auth_config)
