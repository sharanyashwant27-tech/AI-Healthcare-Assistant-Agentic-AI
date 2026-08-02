"""Medical Knowledge Agent — hybrid Vector RAG + GraphRAG."""

from typing import Any, Dict

from agents.base import BaseAgent
from core.config import settings
from i18n.languages import normalize_language
from rag.hybrid import HybridRetriever


class MedicalKnowledgeAgent(BaseAgent):
    name = "medical_knowledge"

    def __init__(self) -> None:
        self.hybrid = HybridRetriever()

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = payload.get("message") or payload.get("query") or ""
        collections = [
            "hospital_guidelines",
            "medical_books",
            "research_papers",
            "drug_database",
        ]
        language = normalize_language(payload.get("language") or "en")
        history_snippet = payload.get("history_snippet") or ""

        result = await self.hybrid.answer(
            query,
            collections=collections,
            symptoms=payload.get("symptoms"),
            patient_key=str(payload["patient_id"]) if payload.get("patient_id") else None,
            language=language,
            history_snippet=history_snippet,
        )

        lower_q = query.lower()
        topics = []
        if any(k in lower_q for k in ["interact", "interaction", "drug"]):
            topics.append("drug_interactions")
        if any(k in lower_q for k in ["treat", "therapy", "guideline", "management"]):
            topics.append("treatment_guidelines")
        if any(k in lower_q for k in ["disease", "what is", "explain"]):
            topics.append("disease_information")

        return {
            "agent": self.name,
            "reply": result["answer"],
            "answer": result["answer"],
            "topics": topics or ["general_medical_knowledge"],
            "sources": result.get("sources", []),
            "citations": result.get("citations", []),
            "confidence": result.get("confidence"),
            "explanation": result.get("explanation"),
            "graph_entities": (result.get("explanation") or {}).get("graph_path") or [],
            "guidelines": ["WHO", "CDC", "Hospital SOPs", "NIH"],
            "mode": "hybrid",
            "disclaimer": settings.medical_disclaimer,
        }
