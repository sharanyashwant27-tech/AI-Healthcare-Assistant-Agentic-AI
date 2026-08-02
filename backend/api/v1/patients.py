"""Patient endpoints."""

from fastapi import APIRouter, HTTPException

from auth.deps import CurrentUser, DbSession
from repositories.patient_repository import PatientRepository
from schemas.patient import PatientResponse

router = APIRouter()


@router.get("/patient", response_model=list[PatientResponse])
async def list_patients(db: DbSession, user: CurrentUser):
    items = await PatientRepository(db).list()
    return [
        PatientResponse(
            id=p.id,
            user_id=p.user_id,
            full_name=p.user.full_name if p.user else None,
            email=p.user.email if p.user else None,
            date_of_birth=p.date_of_birth,
            gender=p.gender,
            blood_group=p.blood_group,
            height_cm=p.height_cm,
            weight_kg=p.weight_kg,
            allergies=p.allergies,
            emergency_contact=p.emergency_contact,
        )
        for p in items
    ]


@router.get("/patient/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: DbSession, user: CurrentUser):
    p = await PatientRepository(db).get(patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientResponse(
        id=p.id,
        user_id=p.user_id,
        full_name=p.user.full_name if p.user else None,
        email=p.user.email if p.user else None,
        date_of_birth=p.date_of_birth,
        gender=p.gender,
        blood_group=p.blood_group,
        height_cm=p.height_cm,
        weight_kg=p.weight_kg,
        allergies=p.allergies,
        emergency_contact=p.emergency_contact,
    )
