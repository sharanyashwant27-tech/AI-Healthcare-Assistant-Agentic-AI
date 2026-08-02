"""Patient-centered healthcare knowledge graph schema for GraphRAG."""

from typing import List

# Hub entity
PATIENT_CENTERED_ENTITIES: List[str] = [
    "Patient",
    "Disease",
    "Symptom",
    "Medicine",
    "Allergy",
    "Doctor",
    "Hospital",
    "LabTest",
    "Insurance",
    "Appointment",
]

"""
Patient
 │
 ├── Disease
 ├── Symptoms
 ├── Medicine
 ├── Allergy
 ├── Doctor
 ├── Hospital
 ├── Lab Test
 ├── Insurance
 └── Appointment
"""

RELATIONSHIPS: List[str] = [
    "HAS_DISEASE",
    "HAS_SYMPTOM",
    "TAKES_MEDICINE",
    "ALLERGIC_TO",
    "TREATED_BY",
    "VISITS",
    "HAS_LAB_TEST",
    "COVERED_BY",
    "BOOKED",
    "PRESCRIBED",
    "REFERRED_TO",
    "ASSOCIATED_WITH",  # disease ↔ disease / complication links
    "MONITORED_BY",  # disease → lab test
    "INDICATED_FOR",  # medicine → disease
]

BENEFITS = [
    "Relationship reasoning across clinical entities",
    "Explainability via traversable care paths",
    "Better retrieval when combined with vector RAG",
    "Faster recommendations from neighborhood expansion",
]

EXAMPLE_PATH = [
    ("Patient", "john", "John"),
    ("Disease", "diabetes", "Diabetes"),
    ("Medicine", "metformin", "Metformin"),
    ("Disease", "kidney_disease", "Kidney Disease"),
    ("LabTest", "creatinine", "Creatinine Test"),
    ("Doctor", "dr_patel", "Dr. Patel"),
    ("Hospital", "city_general", "City General Hospital"),
]
