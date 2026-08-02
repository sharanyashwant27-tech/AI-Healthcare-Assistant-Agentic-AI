"""Patient and doctor schemas."""

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class PatientResponse(BaseModel):
    id: int
    user_id: int
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    allergies: Optional[str] = None
    emergency_contact: Optional[str] = None

    model_config = {"from_attributes": True}


class DoctorResponse(BaseModel):
    id: int
    user_id: int
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    specialty: str
    hospital_name: Optional[str] = None
    years_experience: int
    consultation_fee: float
    rating: float
    is_available: bool
    bio: Optional[str] = None

    model_config = {"from_attributes": True}


class DashboardResponse(BaseModel):
    role: str
    features: List[str] = []
    stats: Dict[str, Any] = Field(default_factory=dict)
    recent_appointments: List[dict] = []
    notifications: List[dict] = []
    alerts: List[str] = []

    # Patient
    health_summary: Optional[Dict[str, Any]] = None
    appointments: List[dict] = []
    prescriptions: List[dict] = []
    reports: List[dict] = []
    reminders: List[dict] = []
    ai_chat: Optional[Dict[str, Any]] = None
    consents: List[dict] = []

    # Doctor
    patient_queue: List[dict] = []
    ai_summaries: List[dict] = []
    risk_alerts: List[dict] = []
    lab_insights: List[dict] = []
    clinical_notes: List[dict] = []

    # Admin
    hospital_analytics: Optional[Dict[str, Any]] = None
    ai_usage: Optional[Dict[str, Any]] = None
    appointment_statistics: Optional[Dict[str, Any]] = None
    operational_metrics: Optional[Dict[str, Any]] = None
