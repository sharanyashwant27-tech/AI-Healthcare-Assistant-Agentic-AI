"""Healthcare content types that are embedded into the vector store."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class EmbeddingContentType:
    key: str
    name: str
    collection: str
    description: str


EMBEDDING_CONTENT_TYPES: List[EmbeddingContentType] = [
    EmbeddingContentType(
        "patient_history",
        "Patient History",
        "patient_records",
        "Longitudinal history, allergies, conditions, and visit summaries",
    ),
    EmbeddingContentType(
        "medical_books",
        "Medical Books",
        "medical_books",
        "Textbooks and clinical handbooks",
    ),
    EmbeddingContentType(
        "clinical_guidelines",
        "Clinical Guidelines",
        "hospital_guidelines",
        "WHO/CDC guidance, SOPs, and clinical protocols",
    ),
    EmbeddingContentType(
        "research_papers",
        "Research Papers",
        "research_papers",
        "Peer-reviewed literature and evidence summaries",
    ),
    EmbeddingContentType(
        "lab_reports",
        "Lab Reports",
        "lab_reports",
        "CBC, chemistry, urine, and other laboratory reports",
    ),
    EmbeddingContentType(
        "doctor_notes",
        "Doctor Notes",
        "doctor_notes",
        "Clinician progress notes and assessments",
    ),
    EmbeddingContentType(
        "prescriptions",
        "Prescriptions",
        "prescriptions",
        "Medication lists, dosages, and pharmacy instructions",
    ),
]

CONTENT_TYPE_BY_KEY: Dict[str, EmbeddingContentType] = {
    c.key: c for c in EMBEDDING_CONTENT_TYPES
}
