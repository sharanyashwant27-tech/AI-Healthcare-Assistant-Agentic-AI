"""Canonical healthcare database table catalog."""

from typing import Any, Dict, List

DATABASE_TABLES: List[Dict[str, Any]] = [
    {
        "name": "Patients",
        "table": "patients",
        "model": "Patient",
        "description": "Patient profiles linked to users",
    },
    {
        "name": "Doctors",
        "table": "doctors",
        "model": "Doctor",
        "description": "Clinician profiles, specialty, and hospital affiliation",
    },
    {
        "name": "Appointments",
        "table": "appointments",
        "model": "Appointment",
        "description": "Scheduled patient–doctor visits",
    },
    {
        "name": "Medicines",
        "table": "medicines",
        "model": "Medicine",
        "description": "Drug reference catalog",
    },
    {
        "name": "Prescriptions",
        "table": "prescriptions",
        "model": "Prescription",
        "description": "Patient prescriptions and OCR analysis",
    },
    {
        "name": "Diseases",
        "table": "diseases",
        "model": "Disease",
        "description": "Disease reference data",
    },
    {
        "name": "Symptoms",
        "table": "symptoms",
        "model": "Symptom",
        "description": "Symptom reference data",
    },
    {
        "name": "LabReports",
        "table": "lab_reports",
        "model": "LabReport",
        "description": "Laboratory report uploads and AI summaries",
    },
    {
        "name": "Insurance",
        "table": "insurance",
        "model": "Insurance",
        "description": "Patient insurance policies and coverage",
    },
    {
        "name": "Hospitals",
        "table": "hospitals",
        "model": "Hospital",
        "description": "Hospital facilities and departments",
    },
    {
        "name": "Notifications",
        "table": "notifications",
        "model": "Notification",
        "description": "In-app / channel notifications",
    },
    {
        "name": "MedicalHistory",
        "table": "medical_history",
        "model": "MedicalHistory",
        "description": "Longitudinal patient conditions and notes",
    },
]
