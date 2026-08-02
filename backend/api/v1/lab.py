"""Lab report endpoint."""

import json
from pathlib import Path

import aiofiles
from fastapi import APIRouter, File, Form, UploadFile

from agents.master import get_master_agent
from core.config import settings
from auth.deps import CurrentUser, DbSession
from models.report import LabReport
from repositories.patient_repository import PatientRepository

router = APIRouter()


@router.post("/lab-report")
async def analyze_lab(
    db: DbSession,
    user: CurrentUser,
    file: UploadFile | None = File(default=None),
    text: str | None = Form(default=None),
):
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = None
    if file is not None:
        file_path = upload_dir / f"lab_{user.id}_{file.filename}"
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await file.read())

    master = get_master_agent()
    result = await master.run_named(
        "lab",
        {"text": text or "", "file_path": str(file_path) if file_path else None},
    )
    patient = await PatientRepository(db).get_by_user(user.id)
    if patient:
        db.add(
            LabReport(
                patient_id=patient.id,
                report_type=result.get("report_type", "general"),
                raw_text=text,
                results_json=json.dumps(result.get("results", {})),
                summary=result.get("summary"),
                abnormalities=json.dumps(result.get("abnormalities", [])),
                file_path=str(file_path) if file_path else None,
            )
        )
        await db.flush()

    from workflows.triggers import trigger_n8n_workflow

    await trigger_n8n_workflow(
        "lab-report",
        {
            "user_id": user.id,
            "text": text or "",
            "file_path": str(file_path) if file_path else None,
            "summary": result.get("summary"),
            "abnormalities": result.get("abnormalities", []),
            "report_type": result.get("report_type", "general"),
        },
    )
    return result
