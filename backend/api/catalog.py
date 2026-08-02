"""Canonical public API catalog."""

from typing import Any, Dict, List

CORE_APIS: List[Dict[str, Any]] = [
    {"method": "POST", "path": "/login", "auth": False, "description": "JWT login"},
    {"method": "POST", "path": "/register", "auth": False, "description": "User registration"},
    {"method": "POST", "path": "/symptom-analysis", "auth": True, "description": "Symptom triage support"},
    {"method": "POST", "path": "/chat", "auth": True, "description": "Master agent chatbot"},
    {"method": "POST", "path": "/appointment", "auth": True, "description": "Book appointment"},
    {"method": "POST", "path": "/prescription", "auth": True, "description": "Prescription OCR/analysis"},
    {"method": "POST", "path": "/lab-report", "auth": True, "description": "Lab report OCR/analysis"},
    {"method": "POST", "path": "/insurance", "auth": True, "description": "Insurance eligibility assist"},
    {"method": "POST", "path": "/reminder", "auth": True, "description": "Medication reminder"},
    {"method": "GET", "path": "/patient", "auth": True, "description": "List patients"},
    {"method": "GET", "path": "/doctor", "auth": True, "description": "List doctors"},
    {"method": "GET", "path": "/dashboard", "auth": True, "description": "Role-aware dashboard"},
]
