"""Shared response schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str
    detail: Optional[Any] = None


class MedicalDisclaimerMixin(BaseModel):
    disclaimer: str = Field(
        default=(
            "This is not a medical diagnosis. Always consult a licensed healthcare "
            "professional. Seek emergency care for severe or life-threatening symptoms."
        )
    )
    uncertainty_note: str = Field(
        default=(
            "AI-generated insights are probabilistic and may be incomplete or incorrect. "
            "Clinical judgment by a licensed professional is required."
        )
    )


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    checks: dict[str, str] = {}
