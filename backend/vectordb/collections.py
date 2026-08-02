"""Canonical vector database collections and provider registry."""

from typing import Dict, List

# Recommended vector databases
VECTOR_DB_PROVIDERS: List[str] = ["qdrant", "pinecone", "milvus"]

# Core + clinical document collections used by embeddings content types
COLLECTIONS: List[str] = [
    "medical_books",
    "research_papers",
    "hospital_guidelines",
    "patient_records",
    "drug_database",
    "insurance_rules",
    "lab_reports",
    "doctor_notes",
    "prescriptions",
]

COLLECTION_DESCRIPTIONS: Dict[str, str] = {
    "medical_books": "Clinical textbooks and medical handbooks",
    "research_papers": "Peer-reviewed research and evidence summaries",
    "hospital_guidelines": "WHO/CDC guidance, hospital SOPs, and clinical guidelines",
    "patient_records": "Patient history embeddings (privacy-controlled / de-identified)",
    "drug_database": "Drug monographs, dosing, and interaction knowledge",
    "insurance_rules": "Insurance coverage rules, claims eligibility, network policies",
    "lab_reports": "Laboratory report embeddings",
    "doctor_notes": "Clinician notes embeddings",
    "prescriptions": "Prescription document embeddings",
}

DEFAULT_RETRIEVAL_COLLECTIONS: List[str] = [
    "hospital_guidelines",
    "medical_books",
    "research_papers",
    "drug_database",
    "patient_records",
    "lab_reports",
    "doctor_notes",
    "prescriptions",
]
