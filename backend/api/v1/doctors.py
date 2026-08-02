"""Doctor endpoints."""

from fastapi import APIRouter, HTTPException, Query

from auth.deps import CurrentUser, DbSession
from repositories.patient_repository import DoctorRepository
from schemas.patient import DoctorResponse

router = APIRouter()


@router.get("/doctor", response_model=list[DoctorResponse])
async def list_doctors(
    db: DbSession,
    user: CurrentUser,
    specialty: str | None = Query(default=None),
):
    items = await DoctorRepository(db).list(specialty=specialty)
    return [
        DoctorResponse(
            id=d.id,
            user_id=d.user_id,
            full_name=d.user.full_name if d.user else None,
            email=d.user.email if d.user else None,
            specialty=d.specialty,
            hospital_name=d.hospital_name,
            years_experience=d.years_experience,
            consultation_fee=d.consultation_fee,
            rating=d.rating,
            is_available=d.is_available,
            bio=d.bio,
        )
        for d in items
    ]


@router.get("/doctor/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: int, db: DbSession, user: CurrentUser):
    d = await DoctorRepository(db).get(doctor_id)
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return DoctorResponse(
        id=d.id,
        user_id=d.user_id,
        full_name=d.user.full_name if d.user else None,
        email=d.user.email if d.user else None,
        specialty=d.specialty,
        hospital_name=d.hospital_name,
        years_experience=d.years_experience,
        consultation_fee=d.consultation_fee,
        rating=d.rating,
        is_available=d.is_available,
        bio=d.bio,
    )
