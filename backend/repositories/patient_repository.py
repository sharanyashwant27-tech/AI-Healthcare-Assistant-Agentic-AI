"""Patient / doctor / appointment repositories."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.appointment import Appointment
from models.doctor import Doctor
from models.patient import Patient
from models.user import User


class PatientRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, patient: Patient) -> Patient:
        self.db.add(patient)
        await self.db.flush()
        await self.db.refresh(patient)
        return patient

    async def get(self, patient_id: int) -> Optional[Patient]:
        result = await self.db.execute(
            select(Patient).options(selectinload(Patient.user)).where(Patient.id == patient_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> Optional[Patient]:
        result = await self.db.execute(select(Patient).where(Patient.user_id == user_id))
        return result.scalar_one_or_none()

    async def list(self, limit: int = 50) -> List[Patient]:
        result = await self.db.execute(
            select(Patient).options(selectinload(Patient.user)).limit(limit)
        )
        return list(result.scalars().all())


class DoctorRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, doctor: Doctor) -> Doctor:
        self.db.add(doctor)
        await self.db.flush()
        await self.db.refresh(doctor)
        return doctor

    async def get(self, doctor_id: int) -> Optional[Doctor]:
        result = await self.db.execute(
            select(Doctor).options(selectinload(Doctor.user)).where(Doctor.id == doctor_id)
        )
        return result.scalar_one_or_none()

    async def list(self, specialty: Optional[str] = None, limit: int = 100) -> List[Doctor]:
        stmt = select(Doctor).options(selectinload(Doctor.user)).order_by(Doctor.specialty).limit(limit)
        if specialty:
            stmt = stmt.where(Doctor.specialty.ilike(f"%{specialty}%"))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class AppointmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, appointment: Appointment) -> Appointment:
        self.db.add(appointment)
        await self.db.flush()
        await self.db.refresh(appointment)
        return appointment

    async def list_for_patient(self, patient_id: int) -> List[Appointment]:
        result = await self.db.execute(
            select(Appointment).where(Appointment.patient_id == patient_id)
        )
        return list(result.scalars().all())

    async def list_recent(self, limit: int = 10) -> List[Appointment]:
        result = await self.db.execute(
            select(Appointment).order_by(Appointment.scheduled_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
