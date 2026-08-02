"""Medication Reminder module — POST/GET /reminder."""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import select

from auth.deps import CurrentUser, DbSession
from models.notification import Notification

router = APIRouter()


class ReminderCreate(BaseModel):
    medicine_name: str = Field(min_length=1, max_length=200)
    dosage: str = "as prescribed"
    schedule: str = Field(default="08:00,20:00", description="Comma-separated HH:MM times")
    notes: Optional[str] = None


class ReminderResponse(BaseModel):
    id: int
    medicine_name: str
    dosage: str
    schedule: str
    message: str
    created_at: str


async def _create_reminder(data: ReminderCreate, db: DbSession, user: CurrentUser) -> ReminderResponse:
    message = (
        f"Reminder set for {data.medicine_name} ({data.dosage}) at {data.schedule}. "
        f"{data.notes or ''} Take only as directed by your clinician."
    )
    note = Notification(
        user_id=user.id,
        channel="reminder",
        title=f"Medication: {data.medicine_name}",
        message=message,
        meta_json=f'{{"schedule":"{data.schedule}","dosage":"{data.dosage}"}}',
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return ReminderResponse(
        id=note.id,
        medicine_name=data.medicine_name,
        dosage=data.dosage,
        schedule=data.schedule,
        message=message,
        created_at=(note.created_at or datetime.now(timezone.utc)).isoformat(),
    )


async def _list_reminders(db: DbSession, user: CurrentUser):
    rows = (
        await db.execute(
            select(Notification)
            .where(Notification.user_id == user.id, Notification.channel == "reminder")
            .order_by(Notification.created_at.desc())
        )
    ).scalars().all()
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in rows
    ]


@router.post("/reminder", response_model=ReminderResponse)
async def create_reminder(data: ReminderCreate, db: DbSession, user: CurrentUser):
    return await _create_reminder(data, db, user)


@router.get("/reminder")
async def list_reminders(db: DbSession, user: CurrentUser):
    return await _list_reminders(db, user)


# Backward-compatible aliases
@router.post("/medication-reminder", response_model=ReminderResponse, include_in_schema=False)
async def create_reminder_alias(data: ReminderCreate, db: DbSession, user: CurrentUser):
    return await _create_reminder(data, db, user)


@router.get("/medication-reminder", include_in_schema=False)
async def list_reminders_alias(db: DbSession, user: CurrentUser):
    return await _list_reminders(db, user)
