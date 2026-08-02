"""Telemedicine session module."""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from auth.deps import CurrentUser, DbSession
from models.notification import Notification
from repositories.patient_repository import DoctorRepository, PatientRepository

router = APIRouter()

# In-memory session registry for demo telemedicine rooms
_SESSIONS: dict[str, dict] = {}


class TelemedicineCreate(BaseModel):
    doctor_id: int
    reason: Optional[str] = "Virtual consultation"
    scheduled_at: Optional[str] = None


class TelemedicineResponse(BaseModel):
    session_id: str
    room_url: str
    doctor_id: int
    patient_id: int
    status: str
    reason: Optional[str] = None
    scheduled_at: str
    instructions: list[str] = Field(default_factory=list)


@router.post("/telemedicine", response_model=TelemedicineResponse)
async def start_telemedicine(data: TelemedicineCreate, db: DbSession, user: CurrentUser):
    patient = await PatientRepository(db).get_by_user(user.id)
    if not patient:
        from models.patient import Patient

        patient = await PatientRepository(db).create(Patient(user_id=user.id))

    doctor = await DoctorRepository(db).get(data.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    session_id = uuid4().hex[:12]
    scheduled = data.scheduled_at or datetime.now(timezone.utc).isoformat()
    room_url = f"/telemedicine/{session_id}"
    _SESSIONS[session_id] = {
        "session_id": session_id,
        "doctor_id": data.doctor_id,
        "patient_id": patient.id,
        "status": "ready",
        "reason": data.reason,
        "scheduled_at": scheduled,
        "room_url": room_url,
    }
    db.add(
        Notification(
            user_id=user.id,
            channel="telemedicine",
            title="Telemedicine session ready",
            message=f"Join virtual visit with Dr. ID {data.doctor_id}: {room_url}",
        )
    )
    await db.flush()
    return TelemedicineResponse(
        session_id=session_id,
        room_url=room_url,
        doctor_id=data.doctor_id,
        patient_id=patient.id,
        status="ready",
        reason=data.reason,
        scheduled_at=scheduled,
        instructions=[
            "Ensure stable internet and a private space",
            "Have medication list and vitals ready if available",
            "This is not for life-threatening emergencies — call emergency services instead",
            "Clinical decisions remain with the licensed clinician",
        ],
    )


@router.get("/telemedicine/{session_id}")
async def get_session(session_id: str, user: CurrentUser):
    session = _SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/telemedicine")
async def list_sessions(user: CurrentUser):
    return list(_SESSIONS.values())[-20:]
