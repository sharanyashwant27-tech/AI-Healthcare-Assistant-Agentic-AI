"""FHIR / HL7 EHR interop APIs."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from auth.deps import CurrentUser, DbSession
from interop.fhir import (
    fhir_capability_statement,
    parse_hl7_oru_lite,
    to_fhir_appointment,
    to_fhir_observation_lab,
    to_fhir_patient,
)
from models.appointment import Appointment
from models.patient import Patient
from models.report import LabReport
from models.user import User

router = APIRouter()


class HL7Ingest(BaseModel):
    message: str = Field(min_length=3, description="Raw HL7 v2 message")


@router.get("/fhir/metadata")
async def fhir_metadata(user: CurrentUser):
    return fhir_capability_statement()


@router.get("/fhir/Patient/{patient_id}")
async def fhir_patient(patient_id: int, db: DbSession, user: CurrentUser):
    row = (
        await db.execute(
            select(Patient).options(selectinload(Patient.user)).where(Patient.id == patient_id)
        )
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Patient not found")
    u: Optional[User] = row.user
    return to_fhir_patient(
        patient_id=row.id,
        full_name=u.full_name if u else None,
        gender=row.gender,
        birth_date=row.date_of_birth.isoformat() if row.date_of_birth else None,
        phone=u.phone if u else None,
        email=u.email if u else None,
    )


@router.get("/fhir/Observation/lab/{report_id}")
async def fhir_lab_observation(report_id: int, db: DbSession, user: CurrentUser):
    row = (await db.execute(select(LabReport).where(LabReport.id == report_id))).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Lab report not found")
    return to_fhir_observation_lab(
        patient_id=row.patient_id,
        report_id=row.id,
        summary=row.summary,
        report_type=row.report_type,
    )


@router.get("/fhir/Appointment/{appointment_id}")
async def fhir_appointment(appointment_id: int, db: DbSession, user: CurrentUser):
    row = (
        await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return to_fhir_appointment(
        appointment_id=row.id,
        patient_id=row.patient_id,
        doctor_id=row.doctor_id,
        scheduled_at=row.scheduled_at.isoformat(),
        status=row.status,
        reason=row.reason,
    )


@router.post("/fhir/hl7/oru")
async def ingest_hl7_oru(data: HL7Ingest, user: CurrentUser):
    parsed = parse_hl7_oru_lite(data.message)
    return {"status": "parsed", "resource": parsed, "note": "Map into LabReport via clinical workflows as needed."}
