"""Compatibility shim — prefer ``auth.security``."""

from auth.security import (
    create_access_token,
    create_refresh_token,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)

__all__ = [
    "create_access_token",
    "create_refresh_token",
    "create_token",
    "decode_token",
    "hash_password",
    "verify_password",
]
