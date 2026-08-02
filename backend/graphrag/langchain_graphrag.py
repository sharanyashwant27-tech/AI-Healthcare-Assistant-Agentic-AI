"""LangChain GraphRAG — Neo4j relationship reasoning + vector retrieval."""

from typing import Any, Dict, List, Optional

from core.config import settings
from core.logging import get_logger
from graphrag.neo4j_client import get_graph_service
from rag.pipeline import get_rag_pipeline
from utils.llm import generate_text

logger = get_logger(__name__)


class LangChainGraphRAG:
    """
    GraphRAG benefits targeted:
    - Relationship reasoning
    - Explainability
    - Better retrieval
    - Faster recommendations
    """

    def __init__(self) -> None:
        self.graph = get_graph_service()
        self.rag = get_rag_pipeline()

    def expand_graph(
        self,
        query: str,
        symptoms: Optional[List[str]] = None,
        patient_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        symptoms = symptoms or []
        reasoning = self.graph.reason(query, patient_key=patient_key)
        disease_hits = self.graph.query_symptoms_to_diseases(symptoms) if symptoms else []
        return {
            **reasoning,
            "symptom_disease_links": disease_hits,
        }

    def _format_path(self, path: List[Dict[str, Any]]) -> str:
        if not path:
            return "No path found"
        parts = []
        for step in path:
            name = step.get("name") or step.get("key")
            label = step.get("label")
            via = step.get("via")
            if via:
                parts.append(f"-[{via}]-> {label}:{name}")
            else:
                parts.append(f"{label}:{name}")
        return " ".join(parts)

    async def aquery(
        self,
        query: str,
        symptoms: Optional[List[str]] = None,
        patient_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        graph_ctx = self.expand_graph(query, symptoms=symptoms, patient_key=patient_key)
        vector_hits = self.rag.retrieve(query, limit=5)

        path_text = self._format_path(graph_ctx.get("explanation_path") or [])
        neighborhood = graph_ctx.get("neighborhood") or {}
        neighbor_text = "\n".join(
            f"{k}: {[n.get('name') or n.get('key') for n in v]}" for k, v in neighborhood.items() if v
        )
        docs_context = "\n\n".join(
            f"[{h.get('collection')}] {h.get('payload', {}).get('text', '')[:600]}"
            for h in vector_hits
        )

        prompt = (
            "You are a GraphRAG medical assistant using a Neo4j knowledge graph.\n"
            "Use relationship paths for explainability and recommendations.\n"
            "Never diagnose with certainty. Explain uncertainty and recommend licensed care.\n\n"
            f"Explainable path:\n{path_text}\n\n"
            f"Patient-centered neighborhood:\n{neighbor_text or 'None'}\n\n"
            f"Symptom→Disease links: {graph_ctx.get('symptom_disease_links')}\n\n"
            f"Vector documents:\n{docs_context or 'None'}\n\n"
            f"Question: {query}\n\n"
            "In the answer, briefly cite the graph path used for reasoning."
        )
        answer = await generate_text(prompt)
        return {
            "answer": answer,
            "graph_entities": graph_ctx.get("keyword_hits") or [],
            "explanation_path": graph_ctx.get("explanation_path") or [],
            "neighborhood": neighborhood,
            "vector_sources": vector_hits,
            "benefits": graph_ctx.get("benefits"),
            "framework": "langchain-graphrag-neo4j",
            "database": "Neo4j",
            "disclaimer": settings.medical_disclaimer,
        }
