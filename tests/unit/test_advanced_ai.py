"""Tests for hybrid retrieval helpers and HITL gating."""

from hitl.service import requires_human_review
from rag.hybrid import build_citations, confidence_from_hits, reciprocal_rank_fusion


def test_rrf_prefers_shared_top_docs():
    a = [
        {"collection": "guidelines", "payload": {"text": "fever protocol A"}, "score": 0.9},
        {"collection": "guidelines", "payload": {"text": "cough note"}, "score": 0.5},
    ]
    b = [
        {"collection": "graph", "payload": {"text": "fever protocol A"}, "score": 0.8},
        {"collection": "graph", "payload": {"text": "rash note"}, "score": 0.4},
    ]
    fused = reciprocal_rank_fusion([a, b], limit=3)
    assert fused
    assert "fever protocol A" in (fused[0].get("payload") or {}).get("text", "")
    assert fused[0]["fusion_score"] > fused[-1]["fusion_score"]


def test_citations_and_confidence():
    hits = [
        {
            "collection": "clinical_guidelines",
            "fusion_score": 0.03,
            "payload": {"text": "Seek urgent care for chest pain.", "source": "AHA"},
        }
    ]
    cites = build_citations(hits)
    assert cites[0]["id"] == "C1"
    conf = confidence_from_hits(hits, explanation_path=[{"step": 1}])
    assert conf["label"] in {"low", "moderate", "high"}
    assert conf["evidence_count"] == 1


def test_hitl_gate_for_high_risk():
    assert requires_human_review("critical") is True
    assert requires_human_review("low", {"label": "high"}, "general") is False
    assert requires_human_review("moderate", {"label": "low"}, "symptom") is True
    assert requires_human_review("low", None, "emergency") is True
