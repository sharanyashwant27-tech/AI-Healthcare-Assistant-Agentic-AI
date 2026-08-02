"""Medical Image Assistant endpoint (non-diagnostic decision support)."""

from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel, Field

from core.config import settings
from auth.deps import CurrentUser
from schemas.common import MedicalDisclaimerMixin
from utils.llm import generate_text
from utils.speech import ocr_image
from utils.storage import get_storage

router = APIRouter()


class ImageAnalysisResponse(MedicalDisclaimerMixin):
    modality: str
    findings: list[str]
    summary: str
    file_uri: Optional[str] = None
    uncertainty_note: str = Field(
        default=(
            "Image analysis is assistive only and may miss or overstate findings. "
            "A licensed radiologist/clinician must interpret imaging."
        )
    )


@router.post("/medical-image", response_model=ImageAnalysisResponse)
async def analyze_medical_image(
    user: CurrentUser,
    file: UploadFile | None = File(default=None),
    modality: str = Form(default="xray"),
    notes: str = Form(default=""),
):
    file_uri = None
    ocr_text = ""
    if file is not None:
        data = await file.read()
        storage = get_storage()
        file_uri = storage.save_bytes(data, file.filename or "image.bin", file.content_type or "image/png")
        # Also keep a local copy for OCR attempt
        local = Path(settings.upload_dir) / Path(file_uri).name
        if not local.exists():
            local.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(local, "wb") as f:
                await f.write(data)
            file_uri_local = str(local)
        else:
            file_uri_local = str(local)
        ocr_text = ocr_image(file_uri_local)

    prompt = (
        f"Assistive medical image review for modality={modality}. "
        f"Clinician notes: {notes}. Extracted text/OCR: {ocr_text[:1500]}. "
        "Provide possible non-diagnostic observations, what to verify, and urgency hints. "
        "Never diagnose with certainty. Recommend licensed clinician review."
    )
    summary = await generate_text(prompt)
    findings = [
        f"Modality noted: {modality}",
        "No definitive diagnosis should be inferred from AI output",
    ]
    if ocr_text:
        findings.append("OCR text detected on image/report overlay")
    if "fracture" in (notes + ocr_text).lower():
        findings.append("User/OCR mentions fracture-related terms — clinician correlation required")

    return ImageAnalysisResponse(
        modality=modality,
        findings=findings,
        summary=summary,
        file_uri=file_uri,
        disclaimer=settings.medical_disclaimer,
    )
