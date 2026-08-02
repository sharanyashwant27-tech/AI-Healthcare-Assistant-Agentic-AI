"""Prescription OCR/analysis endpoint."""

import json
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, Form, UploadFile

from agents.master import get_master_agent
from core.config import settings
from auth.deps import CurrentUser, DbSession
from models.medicine import Prescription
from repositories.patient_repository import PatientRepository

router = APIRouter()


@router.post("/prescription")
async def analyze_prescription(
    db: DbSession,
    user: CurrentUser,
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
    allergies: str | None = Form(default=None),
):
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = None
    if file is not None:
        file_path = upload_dir / f"rx_{user.id}_{file.filename}"
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await file.read())

    master = get_master_agent()
    result = await master.run_named(
        "prescription",
        {
            "text": text or "",
            "file_path": str(file_path) if file_path else None,
            "allergies": allergies or "",
        },
    )

    patient = await PatientRepository(db).get_by_user(user.id)
    if patient:
        db.add(
            Prescription(
                patient_id=patient.id,
                raw_text=text,
                medicines_json=json.dumps(result.get("medicines", [])),
                dosage=result.get("dosage"),
                duration=result.get("duration"),
                analysis_json=json.dumps(result.get("issues", {})),
                file_path=str(file_path) if file_path else None,
            )
        )
        await db.flush()

    from workflows.triggers import trigger_n8n_workflow

    await trigger_n8n_workflow(
        "prescription",
        {
            "user_id": user.id,
            "text": text or "",
            "file_path": str(file_path) if file_path else None,
            "allergies": allergies or "",
            "medicines": result.get("medicines", []),
            "issues": result.get("issues", {}),
        },
    )
    return result
