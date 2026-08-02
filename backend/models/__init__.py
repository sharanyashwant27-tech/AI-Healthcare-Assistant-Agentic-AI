"""SQLAlchemy models — canonical healthcare tables."""

from models.appointment import Appointment
from models.audit import AuditLog
from models.catalog import DATABASE_TABLES
from models.consent import ConsentRecord
from models.disease import Disease, Symptom
from models.doctor import Doctor
from models.hitl import HitlReview
from models.hospital import Hospital
from models.insurance import Insurance
from models.medical_history import MedicalHistory
from models.medicine import Medicine, Prescription
from models.notification import Notification
from models.patient import Patient
from models.report import LabReport
from models.user import Role, User, user_roles

__all__ = [
    "DATABASE_TABLES",
    "User",
    "Role",
    "user_roles",
    "Patient",
    "Doctor",
    "Hospital",
    "Appointment",
    "Symptom",
    "Disease",
    "Medicine",
    "Prescription",
    "LabReport",
    "Insurance",
    "Notification",
    "MedicalHistory",
    "ConsentRecord",
    "HitlReview",
    "AuditLog",
]
