"""Appointment endpoints."""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from agents.master import get_master_agent
from auth.deps import CurrentUser, DbSession
from models.appointment import Appointment
from repositories.patient_repository import AppointmentRepository, PatientRepository
from schemas.chat import AppointmentCreate, AppointmentResponse

router = APIRouter()


@router.post("/appointment", response_model=AppointmentResponse)
async def create_appointment(data: AppointmentCreate, db: DbSession, user: CurrentUser):
    patient_repo = PatientRepository(db)
    patient = await patient_repo.get_by_user(user.id)
    if not patient:
        # auto-create patient profile for non-patient roles testing
        from models.patient import Patient

        patient = await patient_repo.create(Patient(user_id=user.id))

    try:
        scheduled = datetime.fromisoformat(data.scheduled_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid scheduled_at datetime") from exc

    from models.doctor import Doctor

    doctor = await db.get(Doctor, data.doctor_id)
    appt = Appointment(
        patient_id=patient.id,
        doctor_id=data.doctor_id,
        hospital_id=doctor.hospital_id if doctor else None,
        scheduled_at=scheduled,
        status="scheduled",
        reason=data.reason,
    )
    created = await AppointmentRepository(db).create(appt)
    master = get_master_agent()
    await master.run_named(
        "appointment",
        {
            "action": "book",
            "doctor_id": data.doctor_id,
            "scheduled_at": data.scheduled_at,
            "reason": data.reason,
        },
    )
    from workflows.triggers import trigger_n8n_workflow

    await trigger_n8n_workflow(
        "appointment",
        {
            "appointment_id": created.id,
            "doctor_id": data.doctor_id,
            "scheduled_at": data.scheduled_at,
            "reason": data.reason,
            "patient_id": patient.id,
        },
    )
    return AppointmentResponse(
        id=created.id,
        patient_id=created.patient_id,
        doctor_id=created.doctor_id,
        scheduled_at=created.scheduled_at.isoformat(),
        status=created.status,
        reason=created.reason,
    )


@router.get("/appointment")
async def list_appointments(db: DbSession, user: CurrentUser):
    patient = await PatientRepository(db).get_by_user(user.id)
    if not patient:
        return []
    items = await AppointmentRepository(db).list_for_patient(patient.id)
    return [
        {
            "id": a.id,
            "doctor_id": a.doctor_id,
            "scheduled_at": a.scheduled_at.isoformat(),
            "status": a.status,
            "reason": a.reason,
        }
        for a in items
    ]
