"""Canonical n8n healthcare workflow catalog."""

from typing import Any, Dict, List

N8N_WORKFLOWS: List[Dict[str, Any]] = [
    {
        "id": "patient-registration",
        "name": "Patient Registration",
        "webhook_path": "patient-registration",
        "file": "patient-registration.json",
        "steps": [
            "Form",
            "Validate",
            "Create Patient",
            "Send Email",
            "Send SMS",
            "Store Database",
        ],
        "description": "Register a patient from a form, notify channels, and persist the record.",
    },
    {
        "id": "appointment",
        "name": "Appointment",
        "webhook_path": "appointment-booking",
        "file": "appointment-booking.json",
        "steps": [
            "Book",
            "Doctor Availability",
            "Calendar",
            "Confirmation",
            "Reminder",
        ],
        "description": "Book an appointment against doctor availability with confirmation and reminder.",
    },
    {
        "id": "emergency",
        "name": "Emergency",
        "webhook_path": "emergency-alert",
        "file": "emergency-alert.json",
        "steps": [
            "Symptoms",
            "Critical Check",
            "Doctor Alert",
            "Ambulance",
            "Hospital",
            "Family Notification",
        ],
        "description": "Escalate critical symptoms to clinician, EMS, hospital, and family contacts.",
    },
    {
        "id": "prescription",
        "name": "Prescription",
        "webhook_path": "prescription-ocr",
        "file": "prescription-ocr.json",
        "steps": [
            "Upload",
            "OCR",
            "AI",
            "Medicine Extraction",
            "Interaction Check",
            "Patient",
        ],
        "description": "OCR a prescription, extract medicines, check interactions, notify the patient.",
    },
    {
        "id": "lab-report",
        "name": "Lab Report",
        "webhook_path": "lab-report-ocr",
        "file": "lab-report-ocr.json",
        "steps": [
            "Upload",
            "OCR",
            "AI Analysis",
            "Doctor",
            "Patient Summary",
        ],
        "description": "OCR and analyze a lab report, alert the doctor, and send a patient summary.",
    },
]

WORKFLOW_BY_ID = {w["id"]: w for w in N8N_WORKFLOWS}
WORKFLOW_BY_PATH = {w["webhook_path"]: w for w in N8N_WORKFLOWS}
