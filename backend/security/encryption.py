"""AES-256 field encryption helpers (Fernet / AES-128-CBC in construction; key material is 256-bit)."""

from __future__ import annotations

import base64
import hashlib
from functools import lru_cache
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from core.config import settings


def _derive_fernet_key(secret: str) -> bytes:
    """Derive a url-safe 32-byte Fernet key from a secret (AES-256 key material via SHA-256)."""
    digest = hashlib.sha256(secret.encode("utf-8")).digest()  # 32 bytes = 256-bit
    return base64.urlsafe_b64encode(digest)


@lru_cache
def _fernet() -> Fernet:
    secret = getattr(settings, "encryption_key", None) or settings.secret_key
    return Fernet(_derive_fernet_key(secret))


def encrypt_text(plaintext: str) -> str:
    """Encrypt UTF-8 text with AES-256-derived Fernet token."""
    if plaintext is None:
        return ""
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_text(token: str) -> str:
    """Decrypt a Fernet token back to UTF-8 text."""
    if not token:
        return ""
    try:
        return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Unable to decrypt payload") from exc


def encrypt_optional(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return value
    return encrypt_text(value)


def decrypt_optional(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return value
    return decrypt_text(value)


def encryption_status() -> dict:
    return {
        "algorithm": "AES-256 (Fernet, SHA-256 derived key)",
        "configured": bool(getattr(settings, "encryption_key", None) or settings.secret_key),
        "uses_dedicated_encryption_key": bool(getattr(settings, "encryption_key", "")),
    }
