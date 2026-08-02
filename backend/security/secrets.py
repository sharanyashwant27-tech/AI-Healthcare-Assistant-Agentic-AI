"""Secrets management helpers — env/vault-oriented, never hardcode secrets in code."""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.config import settings


SENSITIVE_SETTING_KEYS = {
    "secret_key",
    "encryption_key",
    "openai_api_key",
    "anthropic_api_key",
    "google_api_key",
    "postgres_password",
    "neo4j_password",
    "qdrant_api_key",
    "pinecone_api_key",
    "minio_secret_key",
    "llama_api_key",
}


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read a secret from settings/environment (placeholder for Vault/KMS integration)."""
    value = getattr(settings, name, None)
    if value is None or value == "":
        return default
    return str(value)


def secrets_status() -> Dict[str, Any]:
    configured = []
    missing = []
    for key in sorted(SENSITIVE_SETTING_KEYS):
        val = getattr(settings, key, None)
        if val:
            configured.append(key)
        else:
            missing.append(key)
    return {
        "provider": "environment (.env) — swap for Vault/KMS in production",
        "configured_keys": configured,
        "unset_optional_keys": [k for k in missing if k not in {"secret_key", "encryption_key"}],
        "tls_recommended": True,
        "note": "Do not commit .env. Rotate SECRET_KEY and ENCRYPTION_KEY regularly.",
    }
