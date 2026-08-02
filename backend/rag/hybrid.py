"""Hybrid retrieval — fuse Vector RAG + GraphRAG (RRF) with confidence + citations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from graphrag.neo4j_client import get_graph_service
from rag.pipeline import get_rag_pipeline
from utils.llm import generate_text


def reciprocal_rank_fusion(
    ranked_lists: List[List[Dict[str, Any]]],
    k: int = 60,
    limit: int = 8,
) -> List[Dict[str, Any]]:
    """RRF over lists of hits that each expose optional `score` and `payload.text`."""
    scores: Dict[str, float] = {}
    docs: Dict[str, Dict[str, Any]] = {}
    for hits in ranked_lists:
        for rank, hit in enumerate(hits):
            payload = hit.get("payload") or {}
            text = (payload.get("text") or hit.get("text") or "")[:800]
            key = f"{hit.get('collection', 'graph')}:{text[:120]}"
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
            if key not in docs:
                docs[key] = {**hit, "fusion_key": key}
    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
    out = []
    for key, fused in ordered:
        item = dict(docs[key])
        item["fusion_score"] = round(fused, 6)
        out.append(item)
    return out


def build_citations(hits: List[Dict[str, Any]], max_items: int = 6) -> List[Dict[str, Any]]:
    citations = []
    for i, hit in enumerate(hits[:max_items], 1):
        payload = hit.get("payload") or {}
        text = payload.get("text") or hit.get("text") or ""
        citations.append(
            {
                "id": f"C{i}",
                "collection": hit.get("collection") or hit.get("source") or "knowledge",
                "quote": text[:280],
                "score": hit.get("fusion_score") or hit.get("score"),
                "source_name": payload.get("source") or payload.get("knowledge_source") or hit.get("collection"),
            }
        )
    return citations


def confidence_from_hits(
    hits: List[Dict[str, Any]],
    explanation_path: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    if not hits and not explanation_path:
        return {"score": 0.25, "label": "low", "rationale": "Little retrieved evidence"}
    top = float(hits[0].get("fusion_score") or hits[0].get("score") or 0.0) if hits else 0.0
    # Normalize rough bands for both cosine (~0-1) and RRF (~0-0.03)
    if top > 1:
        top = min(1.0, top / 100.0)
    if top < 0.02 and hits:
        # RRF-scale
        band = min(0.9, 0.45 + top * 15)
    else:
        band = max(0.2, min(0.92, top if top > 0.05 else 0.4 + top))
    if explanation_path:
        band = min(0.95, band + 0.08)
    label = "high" if band >= 0.75 else ("moderate" if band >= 0.45 else "low")
    return {
        "score": round(band, 3),
        "label": label,
        "rationale": "Derived from hybrid retrieval strength and graph path presence",
        "evidence_count": len(hits),
        "graph_path_steps": len(explanation_path or []),
    }


class HybridRetriever:
    """Combine vector RAG hits with graph neighborhood evidence."""

    def __init__(self) -> None:
        self.rag = get_rag_pipeline()
        self.graph = get_graph_service()

    def retrieve(
        self,
        query: str,
        *,
        collections: Optional[List[str]] = None,
        symptoms: Optional[List[str]] = None,
        patient_key: Optional[str] = None,
        limit: int = 8,
    ) -> Dict[str, Any]:
        vector_hits = self.rag.retrieve(query, collections=collections, limit=limit)
        reasoning = self.graph.reason(query, patient_key=patient_key)
        explanation_path = reasoning.get("explanation_path") or []
        path_docs = []
        if explanation_path:
            path_text = " -> ".join(
                str(s.get("name") or s.get("key")) for s in explanation_path if s.get("name") or s.get("key")
            )
            path_docs.append(
                {
                    "collection": "knowledge_graph",
                    "score": 0.85,
                    "payload": {
                        "text": f"Graph evidence path: {path_text}",
                        "source": "Neo4j GraphRAG",
                        "knowledge_source": "graph",
                    },
                }
            )
        if symptoms:
            for d in self.graph.query_symptoms_to_diseases(symptoms)[:3]:
                path_docs.append(
                    {
                        "collection": "knowledge_graph",
                        "score": 0.7,
                        "payload": {
                            "text": f"Symptom–disease association: {d}",
                            "source": "Neo4j",
                            "knowledge_source": "graph",
                        },
                    }
                )

        fused = reciprocal_rank_fusion([vector_hits, path_docs], limit=limit)
        citations = build_citations(fused)
        confidence = confidence_from_hits(fused, explanation_path)
        return {
            "hits": fused,
            "vector_hits": vector_hits,
            "graph_hits": path_docs,
            "explanation_path": explanation_path,
            "neighborhood": reasoning.get("neighborhood") or {},
            "citations": citations,
            "confidence": confidence,
            "mode": "hybrid_rrf",
        }

    async def answer(
        self,
        query: str,
        *,
        collections: Optional[List[str]] = None,
        symptoms: Optional[List[str]] = None,
        patient_key: Optional[str] = None,
        language: str = "en",
        history_snippet: str = "",
    ) -> Dict[str, Any]:
        bundle = self.retrieve(
            query,
            collections=collections,
            symptoms=symptoms,
            patient_key=patient_key,
        )
        evidence_blocks = []
        for c in bundle["citations"]:
            evidence_blocks.append(f"[{c['id']}] ({c['source_name']}) {c['quote']}")
        path = bundle.get("explanation_path") or []
        path_text = " -> ".join(str(s.get("name") or s.get("key")) for s in path) if path else "n/a"

        lang_note = (
            f"Respond in language code '{language}'."
            if language and language != "en"
            else "Respond in clear English."
        )
        prompt = (
            "You are a hybrid RAG + GraphRAG medical assistant.\n"
            "Use retrieved evidence first. Never diagnose with certainty.\n"
            "Cite evidence using [C1], [C2], ... markers.\n"
            "Explain which graph path or documents support the answer (explainable AI).\n"
            f"{lang_note}\n\n"
            f"Conversation memory (recent):\n{history_snippet or 'None'}\n\n"
            f"Explainable graph path: {path_text}\n\n"
            f"Evidence:\n" + ("\n".join(evidence_blocks) or "None") + "\n\n"
            f"Question: {query}\n\n"
            "Return: answer with citations, uncertainty, and recommendation to consult a clinician."
        )
        answer = await generate_text(prompt)
        return {
            "answer": answer,
            "reply": answer,
            "sources": bundle["hits"],
            "citations": bundle["citations"],
            "confidence": bundle["confidence"],
            "explanation": {
                "method": "Hybrid Vector RAG + GraphRAG (RRF)",
                "graph_path": path,
                "evidence_used": bundle["citations"],
                "neighborhood": bundle.get("neighborhood"),
            },
            "mode": "hybrid",
            "disclaimer": "Informational only — not a diagnosis.",
        }
