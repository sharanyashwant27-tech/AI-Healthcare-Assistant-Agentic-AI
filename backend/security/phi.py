"""PHI / PII masking for AI prompts (HIPAA/GDPR-aware handling)."""

from __future__ import annotations

import re
from typing import Dict, Tuple

# Patterns intentionally conservative — replace identifiers before LLM calls.
_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[REDACTED_EMAIL]"),
    (r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
    (r"\b(?:MRN|Member ID|Policy)[:#\s-]*[A-Za-z0-9-]{4,}\b", "[REDACTED_ID]",),
    (r"\b(?:patient|name)\s*[:=]\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", "[REDACTED_NAME]"),
    (r"\b\d{1,5}\s+[A-Za-z0-9.'\s]{3,40}\b(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr)\b", "[REDACTED_ADDRESS]"),
    (r"\b(?:dob|date of birth)\s*[:=]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", "[REDACTED_DOB]"),
)


def mask_phi(text: str) -> str:
    """Mask common PHI/PII patterns in text sent to external LLMs."""
    if not text:
        return text
    masked = text
    for pattern, replacement in _PATTERNS:
        masked = re.sub(pattern, replacement, masked, flags=re.IGNORECASE)
    return masked


def mask_phi_with_report(text: str) -> Tuple[str, Dict[str, int]]:
    report: Dict[str, int] = {}
    masked = text or ""
    for pattern, replacement in _PATTERNS:
        matches = re.findall(pattern, masked, flags=re.IGNORECASE)
        if matches:
            report[replacement] = report.get(replacement, 0) + len(matches)
        masked = re.sub(pattern, replacement, masked, flags=re.IGNORECASE)
    return masked, report
