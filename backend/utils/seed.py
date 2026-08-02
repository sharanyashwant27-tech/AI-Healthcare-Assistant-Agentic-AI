"""Database seed data for demo users and medical references."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.security import hash_password
from core.logging import get_logger
from models.disease import Disease, Symptom
from models.doctor import Doctor
from models.hospital import Hospital
from models.medicine import Medicine
from models.patient import Patient
from models.user import Role, User
from rag.pipeline import get_rag_pipeline

logger = get_logger(__name__)


async def _get_or_create_role(db: AsyncSession, name: str) -> Role:
    result = await db.execute(select(Role).where(Role.name == name))
    role = result.scalar_one_or_none()
    if role:
        return role
    role = Role(name=name, description=f"{name.title()} role")
    db.add(role)
    await db.flush()
    return role


async def _ensure_hospital(db: AsyncSession) -> Hospital:
    result = await db.execute(select(Hospital).where(Hospital.name == "City General Hospital"))
    hospital = result.scalar_one_or_none()
    if hospital:
        return hospital
    hospital = Hospital(
        name="City General Hospital",
        code="CGH-001",
        address="100 Care Avenue",
        city="Metropolis",
        state="Demo State",
        country="IN",
        phone="+1-555-0100",
        email="care@citygeneral.example",
        departments="Emergency,Internal Medicine,Cardiology,Neurology,Lab,Pharmacy",
        emergency_available=True,
        is_active=True,
    )
    db.add(hospital)
    await db.flush()
    return hospital


async def _ensure_reference_data(db: AsyncSession) -> Hospital:
    hospital = await _ensure_hospital(db)

    if (await db.execute(select(Symptom).limit(1))).scalar_one_or_none() is None:
        db.add_all(
            [
                Symptom(name="Fever", description="Elevated body temperature", body_system="systemic"),
                Symptom(name="Cough", description="Respiratory reflex", body_system="respiratory"),
                Symptom(name="Headache", description="Head pain", body_system="neurological"),
                Symptom(
                    name="Chest Pain",
                    description="Pain in chest region",
                    body_system="cardiac",
                    severity_hint="high",
                ),
            ]
        )

    if (await db.execute(select(Disease).limit(1))).scalar_one_or_none() is None:
        db.add_all(
            [
                Disease(
                    name="Influenza",
                    icd_code="J11",
                    description="Viral respiratory infection",
                    common_symptoms="fever,cough,fatigue",
                    specialist="Internal Medicine",
                    urgency_level="routine",
                ),
                Disease(
                    name="Migraine",
                    icd_code="G43",
                    description="Neurological headache disorder",
                    common_symptoms="headache,nausea,light sensitivity",
                    specialist="Neurology",
                    urgency_level="routine",
                ),
            ]
        )

    if (await db.execute(select(Medicine).limit(1))).scalar_one_or_none() is None:
        db.add_all(
            [
                Medicine(
                    name="Paracetamol",
                    generic_name="Acetaminophen",
                    drug_class="analgesic",
                    common_dosage="500mg",
                ),
                Medicine(
                    name="Ibuprofen",
                    generic_name="Ibuprofen",
                    drug_class="nsaid",
                    common_dosage="400mg",
                ),
                Medicine(
                    name="Amoxicillin",
                    generic_name="Amoxicillin",
                    drug_class="antibiotic",
                    common_dosage="500mg",
                ),
            ]
        )

    await db.flush()
    return hospital


async def seed_database(db: AsyncSession) -> None:
    hospital = await _ensure_reference_data(db)

    existing = await db.execute(select(User).where(User.email == "patient@example.com"))
    if existing.scalar_one_or_none():
        # Keep doctor linked to hospital even on re-seed skip
        doctor = (
            await db.execute(select(Doctor).where(Doctor.license_number == "LIC-DOC-0001"))
        ).scalar_one_or_none()
        if doctor and not doctor.hospital_id:
            doctor.hospital_id = hospital.id
            doctor.hospital_name = hospital.name
            await db.flush()
        logger.info("seed_skipped_existing_demo_users")
        return

    roles = {
        name: await _get_or_create_role(db, name)
        for name in ["patient", "doctor", "admin", "receptionist"]
    }

    admin = User(
        email="admin@example.com",
        hashed_password=hash_password("Admin@12345"),
        full_name="System Admin",
        is_active=True,
        is_verified=True,
        roles=[roles["admin"]],
    )
    patient_user = User(
        email="patient@example.com",
        hashed_password=hash_password("Patient@12345"),
        full_name="Demo Patient",
        phone="+1-555-0100",
        is_active=True,
        is_verified=True,
        roles=[roles["patient"]],
    )
    doctor_user = User(
        email="doctor@example.com",
        hashed_password=hash_password("Doctor@12345"),
        full_name="Dr. Ananya Sharma",
        phone="+1-555-0101",
        is_active=True,
        is_verified=True,
        roles=[roles["doctor"]],
    )
    db.add_all([admin, patient_user, doctor_user])
    await db.flush()

    patient_profile = await db.execute(select(Patient).where(Patient.user_id == patient_user.id))
    if patient_profile.scalar_one_or_none() is None:
        db.add(
            Patient(
                user_id=patient_user.id,
                gender="female",
                blood_group="O+",
                height_cm=162,
                weight_kg=58,
                allergies="Penicillin",
                emergency_contact="Family Contact",
                emergency_phone="+1-555-0199",
            )
        )

    doctor_profile = await db.execute(select(Doctor).where(Doctor.user_id == doctor_user.id))
    if doctor_profile.scalar_one_or_none() is None:
        db.add(
            Doctor(
                user_id=doctor_user.id,
                hospital_id=hospital.id,
                specialty="Internal Medicine",
                license_number="LIC-DOC-0001",
                hospital_name=hospital.name,
                years_experience=12,
                consultation_fee=50.0,
                bio="Board-certified internist focusing on preventive care.",
                is_available=True,
                rating=4.8,
            )
        )

    await db.flush()

    try:
        rag = get_rag_pipeline()
        counts = rag.ingest_knowledge_corpus()
        logger.info("seed_rag_corpus", counts=counts)
    except Exception as exc:  # noqa: BLE001
        logger.warning("seed_rag_skipped", error=str(exc))

    logger.info("seed_completed")
