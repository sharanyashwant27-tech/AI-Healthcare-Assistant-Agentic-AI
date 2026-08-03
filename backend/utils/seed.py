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

# Specialty catalog used for demo doctors and appointment booking.
SPECIALTY_DOCTORS = [
    {
        "email": "doctor@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Ananya Sharma",
        "phone": "+1-555-0101",
        "specialty": "Internal Medicine",
        "license_number": "LIC-DOC-0001",
        "years_experience": 12,
        "consultation_fee": 50.0,
        "rating": 4.8,
        "bio": "Board-certified internist focusing on preventive care.",
    },
    {
        "email": "cardio@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Rohan Mehta",
        "phone": "+1-555-0201",
        "specialty": "Cardiology",
        "license_number": "LIC-DOC-CARDIO-01",
        "years_experience": 15,
        "consultation_fee": 90.0,
        "rating": 4.9,
        "bio": "Interventional cardiologist for chest pain, hypertension, and heart failure.",
    },
    {
        "email": "gastro@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Priya Nair",
        "phone": "+1-555-0202",
        "specialty": "Gastroenterology",
        "license_number": "LIC-DOC-GASTRO-01",
        "years_experience": 11,
        "consultation_fee": 80.0,
        "rating": 4.7,
        "bio": "Specialist in acid reflux, IBS, liver disorders, and endoscopy.",
    },
    {
        "email": "ent@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Kabir Singh",
        "phone": "+1-555-0203",
        "specialty": "ENT",
        "license_number": "LIC-DOC-ENT-01",
        "years_experience": 10,
        "consultation_fee": 70.0,
        "rating": 4.6,
        "bio": "Ear, nose, and throat specialist for sinusitis, hearing loss, and tonsillitis.",
    },
    {
        "email": "neuro@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Meera Iyer",
        "phone": "+1-555-0204",
        "specialty": "Neurology",
        "license_number": "LIC-DOC-NEURO-01",
        "years_experience": 14,
        "consultation_fee": 95.0,
        "rating": 4.8,
        "bio": "Neurologist for migraine, seizures, stroke follow-up, and neuropathy.",
    },
    {
        "email": "ortho@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Arjun Desai",
        "phone": "+1-555-0205",
        "specialty": "Orthopedics",
        "license_number": "LIC-DOC-ORTHO-01",
        "years_experience": 13,
        "consultation_fee": 85.0,
        "rating": 4.7,
        "bio": "Orthopedic surgeon for joint pain, fractures, and sports injuries.",
    },
    {
        "email": "derma@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Sneha Kapoor",
        "phone": "+1-555-0206",
        "specialty": "Dermatology",
        "license_number": "LIC-DOC-DERMA-01",
        "years_experience": 9,
        "consultation_fee": 65.0,
        "rating": 4.8,
        "bio": "Dermatologist for acne, eczema, hair loss, and skin infections.",
    },
    {
        "email": "pedia@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Neha Joshi",
        "phone": "+1-555-0207",
        "specialty": "Pediatrics",
        "license_number": "LIC-DOC-PEDIA-01",
        "years_experience": 8,
        "consultation_fee": 60.0,
        "rating": 4.9,
        "bio": "Pediatrician for child wellness, immunizations, and common infections.",
    },
    {
        "email": "pulmo@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Vikram Rao",
        "phone": "+1-555-0208",
        "specialty": "Pulmonology",
        "license_number": "LIC-DOC-PULMO-01",
        "years_experience": 12,
        "consultation_fee": 80.0,
        "rating": 4.6,
        "bio": "Lung specialist for asthma, COPD, cough, and sleep apnea.",
    },
    {
        "email": "gyn@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Aisha Khan",
        "phone": "+1-555-0209",
        "specialty": "Gynecology",
        "license_number": "LIC-DOC-GYN-01",
        "years_experience": 16,
        "consultation_fee": 85.0,
        "rating": 4.8,
        "bio": "OB-GYN for women's health, prenatal care, and reproductive concerns.",
    },
    {
        "email": "ophtho@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Farhan Ali",
        "phone": "+1-555-0210",
        "specialty": "Ophthalmology",
        "license_number": "LIC-DOC-OPHTHO-01",
        "years_experience": 11,
        "consultation_fee": 75.0,
        "rating": 4.7,
        "bio": "Eye specialist for vision checks, cataracts, and infections.",
    },
    {
        "email": "psych@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Leah Mendes",
        "phone": "+1-555-0211",
        "specialty": "Psychiatry",
        "license_number": "LIC-DOC-PSYCH-01",
        "years_experience": 10,
        "consultation_fee": 90.0,
        "rating": 4.8,
        "bio": "Psychiatrist for anxiety, depression, and sleep-related care.",
    },
    {
        "email": "endo@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Sanjay Patel",
        "phone": "+1-555-0212",
        "specialty": "Endocrinology",
        "license_number": "LIC-DOC-ENDO-01",
        "years_experience": 14,
        "consultation_fee": 85.0,
        "rating": 4.7,
        "bio": "Endocrinologist for diabetes, thyroid disorders, and hormones.",
    },
    {
        "email": "uro@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Imran Qureshi",
        "phone": "+1-555-0213",
        "specialty": "Urology",
        "license_number": "LIC-DOC-URO-01",
        "years_experience": 12,
        "consultation_fee": 80.0,
        "rating": 4.6,
        "bio": "Urologist for kidney stones, UTIs, and prostate concerns.",
    },
    {
        "email": "dental@example.com",
        "password": "Doctor@12345",
        "full_name": "Dr. Rhea Fernandes",
        "phone": "+1-555-0214",
        "specialty": "Dental",
        "license_number": "LIC-DOC-DENTAL-01",
        "years_experience": 7,
        "consultation_fee": 55.0,
        "rating": 4.5,
        "bio": "Dental care for tooth pain, cavities, and oral hygiene.",
    },
]


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
    departments = (
        "Emergency,Internal Medicine,Cardiology,Gastroenterology,ENT,Neurology,"
        "Orthopedics,Dermatology,Pediatrics,Pulmonology,Gynecology,Ophthalmology,"
        "Psychiatry,Endocrinology,Urology,Dental,Lab,Pharmacy"
    )
    if hospital:
        hospital.departments = departments
        hospital.emergency_available = True
        await db.flush()
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
        departments=departments,
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


async def _ensure_specialty_doctors(db: AsyncSession, hospital: Hospital) -> int:
    """Idempotently create doctors across major specialty categories."""
    doctor_role = await _get_or_create_role(db, "doctor")
    created = 0

    for item in SPECIALTY_DOCTORS:
        user = (
            await db.execute(select(User).where(User.email == item["email"]))
        ).scalar_one_or_none()
        if user is None:
            user = User(
                email=item["email"],
                hashed_password=hash_password(item["password"]),
                full_name=item["full_name"],
                phone=item["phone"],
                is_active=True,
                is_verified=True,
                roles=[doctor_role],
            )
            db.add(user)
            await db.flush()
            created += 1
        elif doctor_role not in (user.roles or []):
            user.roles = list(user.roles or []) + [doctor_role]
            await db.flush()

        doctor = (
            await db.execute(select(Doctor).where(Doctor.user_id == user.id))
        ).scalar_one_or_none()
        if doctor is None:
            # Prefer license uniqueness for re-runs
            by_license = (
                await db.execute(select(Doctor).where(Doctor.license_number == item["license_number"]))
            ).scalar_one_or_none()
            if by_license is None:
                db.add(
                    Doctor(
                        user_id=user.id,
                        hospital_id=hospital.id,
                        specialty=item["specialty"],
                        license_number=item["license_number"],
                        hospital_name=hospital.name,
                        years_experience=item["years_experience"],
                        consultation_fee=item["consultation_fee"],
                        bio=item["bio"],
                        is_available=True,
                        rating=item["rating"],
                    )
                )
                created += 1
        else:
            doctor.hospital_id = hospital.id
            doctor.hospital_name = hospital.name
            doctor.specialty = item["specialty"]
            doctor.bio = item["bio"]
            doctor.is_available = True
            doctor.years_experience = item["years_experience"]
            doctor.consultation_fee = item["consultation_fee"]
            doctor.rating = item["rating"]

    await db.flush()
    return created


async def seed_database(db: AsyncSession) -> None:
    hospital = await _ensure_reference_data(db)
    doctors_touched = await _ensure_specialty_doctors(db, hospital)

    existing = await db.execute(select(User).where(User.email == "patient@example.com"))
    if existing.scalar_one_or_none():
        logger.info(
            "seed_skipped_existing_demo_users",
            specialty_doctors_upserted=doctors_touched,
            specialties=len(SPECIALTY_DOCTORS),
        )
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
    db.add_all([admin, patient_user])
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

    await db.flush()

    try:
        rag = get_rag_pipeline()
        counts = rag.ingest_knowledge_corpus()
        logger.info("seed_rag_corpus", counts=counts)
    except Exception as exc:  # noqa: BLE001
        logger.warning("seed_rag_skipped", error=str(exc))

    logger.info("seed_completed", specialty_doctors=len(SPECIALTY_DOCTORS))
