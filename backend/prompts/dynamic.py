"""Dynamic prompting — adapt instructions by patient context."""

from typing import Any, Dict, Optional

# Patient Type → Age → Disease → Country → Hospital Protocol
DYNAMIC_PROMPT_DIMENSIONS = [
    "patient_type",
    "age",
    "disease",
    "country",
    "hospital_protocol",
]

DEFAULT_PROTOCOLS: Dict[str, str] = {
    "IN": "Follow Indian clinical practice norms; prefer ICMR/MoHFW-aligned general guidance when available.",
    "US": "Follow US-oriented general guidance; prefer CDC/USPSTF-aligned framing when available.",
    "UK": "Follow UK-oriented general guidance; prefer NICE-aligned framing when available.",
    "GLOBAL": "Prefer WHO-aligned general guidance when country-specific protocol is unspecified.",
}


def resolve_hospital_protocol(
    country: Optional[str] = None,
    hospital_protocol: Optional[str] = None,
) -> str:
    if hospital_protocol:
        return hospital_protocol
    code = (country or "GLOBAL").upper().strip()
    if len(code) > 3:
        # allow full country names
        mapping = {
            "INDIA": "IN",
            "UNITED STATES": "US",
            "USA": "US",
            "UNITED KINGDOM": "UK",
            "ENGLAND": "UK",
        }
        code = mapping.get(code, "GLOBAL")
    return DEFAULT_PROTOCOLS.get(code, DEFAULT_PROTOCOLS["GLOBAL"])


def build_dynamic_context(payload: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    payload = payload or {}
    patient_type = str(payload.get("patient_type") or payload.get("role") or "patient")
    age = payload.get("age")
    disease = str(payload.get("disease") or payload.get("known_condition") or "unspecified")
    country = str(payload.get("country") or "GLOBAL")
    protocol = resolve_hospital_protocol(country, payload.get("hospital_protocol"))
    return {
        "patient_type": patient_type,
        "age": str(age if age is not None else "unknown"),
        "disease": disease,
        "country": country,
        "hospital_protocol": protocol,
    }


def format_dynamic_block(payload: Optional[Dict[str, Any]] = None) -> str:
    ctx = build_dynamic_context(payload)
    return (
        "Dynamic prompting context:\n"
        f"- Patient Type: {ctx['patient_type']}\n"
        f"- Age: {ctx['age']}\n"
        f"- Disease: {ctx['disease']}\n"
        f"- Country: {ctx['country']}\n"
        f"- Hospital Protocol: {ctx['hospital_protocol']}\n"
        "Adapt tone and recommendations to this context while keeping safety rules."
    )
