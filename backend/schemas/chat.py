"""Chat and agent request/response schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from schemas.common import MedicalDisclaimerMixin


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    conversation_id: Optional[str] = None
    patient_id: Optional[int] = None
    language: Optional[str] = "en"
    enable_hitl: bool = True
    context: Optional[Dict[str, Any]] = None


class ChatResponse(MedicalDisclaimerMixin):
    conversation_id: str
    reply: str
    agent: str
    orchestrator: str = "master"
    intent: Optional[str] = None
    plan: List[str] = []
    sources: List[Dict[str, Any]] = []
    citations: List[Dict[str, Any]] = []
    confidence: Optional[Dict[str, Any]] = None
    explanation: Optional[Dict[str, Any]] = None
    risk_level: Optional[str] = None
    human_review: Optional[Dict[str, Any]] = None
    language: Optional[str] = "en"
    memory: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    architecture: Dict[str, Any] = {}
    review_id: Optional[str] = None


class SymptomAnalysisRequest(BaseModel):
    symptoms: List[str] = Field(min_length=1)
    duration: Optional[str] = None
    severity: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    medical_history: Optional[str] = None
    current_medicines: Optional[str] = None
    allergies: Optional[str] = None
    additional_notes: Optional[str] = None
    patient_type: Optional[str] = "patient"
    disease: Optional[str] = None
    country: Optional[str] = None
    hospital_protocol: Optional[str] = None


class SymptomAnalysisResponse(MedicalDisclaimerMixin):
    possible_conditions: List[Dict[str, Any]]
    risk_level: str
    risk_score: int = 50
    next_action: Optional[str] = None
    recommended_specialist: Optional[str] = None
    urgency: str
    advice: str
    emergency_flags: List[str] = []


class AppointmentCreate(BaseModel):
    doctor_id: int
    scheduled_at: str
    reason: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    scheduled_at: str
    status: str
    reason: Optional[str] = None

    model_config = {"from_attributes": True}


class NutritionRequest(BaseModel):
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: str = "moderate"
    goals: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None


class NutritionResponse(MedicalDisclaimerMixin):
    bmi: float
    bmi_category: str
    daily_calories: int
    water_intake_liters: float
    diet_plan: Dict[str, Any]
    exercise_plan: List[str]


class InsuranceRequest(BaseModel):
    policy_number: str
    provider_name: Optional[str] = None
    procedure: Optional[str] = None
    hospital_name: Optional[str] = None


class InsuranceResponse(MedicalDisclaimerMixin):
    is_valid: bool
    coverage_summary: str
    claim_eligible: bool
    network_status: str
    details: Dict[str, Any] = {}


class EmergencyRequest(BaseModel):
    symptoms: List[str]
    description: Optional[str] = None
    location: Optional[str] = None
    patient_id: Optional[int] = None


class EmergencyResponse(MedicalDisclaimerMixin):
    is_emergency: bool
    emergency_type: Optional[str] = None
    immediate_actions: List[str]
    alert_sent: bool
    message: str
