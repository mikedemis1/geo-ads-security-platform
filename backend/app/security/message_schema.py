# backend/app/security/message_schema.py

import json
import secrets
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.security.crypto_engine import CryptoEngine, get_crypto_engine


class NodeRole(str, Enum):
    CONTROLLER = "controller"
    ZONE_DISPLAY = "zone_display"
    SYSTEM = "system"


class MessageHeader(BaseModel):
    node_id: str = Field(..., description="Logical node id, e.g. 'controller-1'")
    zone_id: Optional[str] = Field(None, description="Zone id (optional)")
    role: NodeRole
    msg_type: str
    timestamp: datetime
    nonce: str
    alg: Optional[str] = Field(None, description="Algorithm name e.g. 'HMAC_SHA256'")
    version: str = Field("1.0", description="Message schema version")


class SignedMessage(BaseModel):
    header: MessageHeader
    payload: Dict[str, Any]
    hmac: str

    def _to_canonical_bytes(self) -> bytes:
        data = {
            "header": json.loads(self.header.model_dump_json()),
            "payload": self.payload,
        }
        json_str = json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return json_str.encode("utf-8")

    def compute_hmac(
        self,
        secret_key: str,
        crypto: Optional[CryptoEngine] = None,
    ) -> str:
        if crypto is None:
            crypto = get_crypto_engine()
        message_bytes = self._to_canonical_bytes()
        signature = crypto.sign(message_bytes, secret_key)
        self.hmac = signature
        return self.hmac

    def verify_hmac(
        self,
        secret_key: str,
        crypto: Optional[CryptoEngine] = None,
    ) -> bool:
        if crypto is None:
            crypto = get_crypto_engine()
        if not self.hmac:
            return False
        message_bytes = self._to_canonical_bytes()
        return crypto.verify(message_bytes, self.hmac, secret_key)

    @classmethod
    def create(
        cls,
        *,
        node_id: str,
        role: NodeRole,
        msg_type: str,
        payload: Dict[str, Any],
        secret_key: str,
        zone_id: Optional[str] = None,
        crypto: Optional[CryptoEngine] = None,
    ) -> "SignedMessage":
        if crypto is None:
            crypto = get_crypto_engine()

        header = MessageHeader(
            node_id=node_id,
            zone_id=zone_id,
            role=role,
            msg_type=msg_type,
            timestamp=datetime.now(timezone.utc),
            nonce=secrets.token_hex(16),
            alg=crypto.algorithm_name,
        )

        msg = cls(header=header, payload=payload, hmac="")
        msg.compute_hmac(secret_key=secret_key, crypto=crypto)
        return msg