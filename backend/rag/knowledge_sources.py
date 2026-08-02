"""Canonical medical knowledge sources mapped to vector collections."""

from dataclasses import dataclass
from typing import Dict, List

from vectordb.collections import DEFAULT_RETRIEVAL_COLLECTIONS

@dataclass(frozen=True)
class KnowledgeSource:
    key: str
    name: str
    collection: str
    description: str


KNOWLEDGE_SOURCES: List[KnowledgeSource] = [
    KnowledgeSource(
        "who",
        "WHO Guidelines",
        "hospital_guidelines",
        "World Health Organization clinical and public-health guidance",
    ),
    KnowledgeSource(
        "cdc",
        "CDC Guidelines",
        "hospital_guidelines",
        "Centers for Disease Control and Prevention guidance",
    ),
    KnowledgeSource(
        "sop",
        "Hospital SOP",
        "hospital_guidelines",
        "Hospital standard operating procedures and triage pathways",
    ),
    KnowledgeSource(
        "drug",
        "Drug Database",
        "drug_database",
        "Medicine monographs, dosing, and interaction notes",
    ),
    KnowledgeSource(
        "books",
        "Medical Books",
        "medical_books",
        "Reference textbooks and clinical handbooks",
    ),
    KnowledgeSource(
        "research",
        "Research Papers",
        "research_papers",
        "Peer-reviewed research and evidence summaries",
    ),
    KnowledgeSource(
        "policies",
        "Hospital Policies",
        "hospital_guidelines",
        "Institutional clinical and administrative policies",
    ),
    KnowledgeSource(
        "insurance",
        "Insurance Rules",
        "insurance_rules",
        "Coverage rules, claim eligibility, and network policies",
    ),
    KnowledgeSource(
        "patient",
        "Patient History",
        "patient_records",
        "Longitudinal history, allergies, conditions, and visit summaries",
    ),
    KnowledgeSource(
        "labs",
        "Lab Reports",
        "lab_reports",
        "CBC, chemistry, urine, and other laboratory reports",
    ),
    KnowledgeSource(
        "notes",
        "Doctor Notes",
        "doctor_notes",
        "Clinician progress notes and assessments",
    ),
    KnowledgeSource(
        "rx",
        "Prescriptions",
        "prescriptions",
        "Medication lists, dosages, and pharmacy instructions",
    ),
]

SOURCE_BY_KEY: Dict[str, KnowledgeSource] = {s.key: s for s in KNOWLEDGE_SOURCES}

PIPELINE_STAGES = [
    "Medical documents",
    "PDF / Text / Word / CSV Loader",
    "Chunking",
    "Embeddings",
    "Vector Database",
    "Retriever",
    "LLM",
    "Answer",
]

__all__ = [
    "KnowledgeSource",
    "KNOWLEDGE_SOURCES",
    "SOURCE_BY_KEY",
    "DEFAULT_RETRIEVAL_COLLECTIONS",
    "PIPELINE_STAGES",
]
