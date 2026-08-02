"""Security package — encryption, PHI masking, consent, secrets."""

from security.consent import CONSENT_TYPES, ConsentService
from security.encryption import decrypt_text, encrypt_text, encryption_status
from security.phi import mask_phi, mask_phi_with_report
from security.secrets import get_secret, secrets_status

__all__ = [
    "CONSENT_TYPES",
    "ConsentService",
    "decrypt_text",
    "encrypt_text",
    "encryption_status",
    "get_secret",
    "mask_phi",
    "mask_phi_with_report",
    "secrets_status",
]
