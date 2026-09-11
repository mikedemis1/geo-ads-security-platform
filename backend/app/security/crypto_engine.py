# backend/app/security/crypto_engine.py

import os
import hmac
import hashlib
from enum import Enum
from typing import Optional, Union


class CryptoMode(str, Enum):
    """
    Supported signing modes.
    - HMAC_SHA256: HMAC over SHA-256 (SHA-2 family).
    - HMAC_SHA3_256: HMAC over SHA3-256 (SHA-3 family).
    """
    HMAC_SHA256 = "HMAC_SHA256"
    HMAC_SHA3_256 = "HMAC_SHA3_256"


def _resolve_mode_from_env() -> CryptoMode:
    """
    Read CRYPTO_MODE from the environment and return a CryptoMode.
    Falls back to HMAC_SHA256 when the value is missing or invalid.
    """
    raw = os.getenv("CRYPTO_MODE", CryptoMode.HMAC_SHA256.value)
    try:
        return CryptoMode(raw)
    except ValueError:
        # A production system should log this as a misconfiguration.
        return CryptoMode.HMAC_SHA256


class CryptoEngine:
    """
    One interface for signing and verification.

    - Used for HMAC today.
    - Can be extended with a post-quantum signature scheme or KEM later
      without changing the call sites (crypto-agility).
    """

    def __init__(self, mode: Union[CryptoMode, str, None] = None) -> None:
        if mode is None:
            mode = _resolve_mode_from_env()

        if isinstance(mode, str):
            try:
                mode = CryptoMode(mode)
            except ValueError as exc:
                raise ValueError(f"Unsupported CRYPTO_MODE: {mode}") from exc

        self.mode: CryptoMode = mode

    @property
    def algorithm_name(self) -> str:
        """
        Algorithm name written into message headers (e.g. "HMAC_SHA256").
        """
        return self.mode.value

    def _get_digestmod(self):
        """
        Return the hashlib function that matches the selected mode.

        """
        if self.mode == CryptoMode.HMAC_SHA256:
            return hashlib.sha256
        elif self.mode == CryptoMode.HMAC_SHA3_256:
            return hashlib.sha3_256
        else:
            # Unreachable as long as every mode is handled above.
            raise ValueError(f"Unsupported crypto mode: {self.mode}")

    @staticmethod
    def _normalize_secret(secret_key: Union[str, bytes]) -> bytes:
        """
        Accept the secret as str or bytes and return bytes.
        """
        if isinstance(secret_key, bytes):
            return secret_key
        return secret_key.encode("utf-8")

    def sign(self, message: bytes, secret_key: Union[str, bytes]) -> str:
        """
        Sign the message with HMAC and return the digest as a hex string.

        - message: the bytes to protect (header + payload).
        - secret_key: the node's shared secret.
        """
        key_bytes = self._normalize_secret(secret_key)
        digestmod = self._get_digestmod()
        mac = hmac.new(key_bytes, message, digestmod=digestmod)
        return mac.hexdigest()

    def verify(self, message: bytes, signature_hex: str, secret_key: Union[str, bytes]) -> bool:
        """
        Verify a signature.

        - Recomputes the HMAC over the message with the secret.
        - Compares in constant time (hmac.compare_digest)
          to avoid timing attacks.
        """
        expected = self.sign(message, secret_key)
        # constant-time compare
        return hmac.compare_digest(expected, signature_hex)


# Shared instance so the whole app uses one CRYPTO_MODE
_engine_singleton: Optional[CryptoEngine] = None


def get_crypto_engine() -> CryptoEngine:
    """
    Return the shared CryptoEngine instance.
    Used everywhere so that one CRYPTO_MODE applies across the app.
    """
    global _engine_singleton
    if _engine_singleton is None:
        _engine_singleton = CryptoEngine()
    return _engine_singleton
