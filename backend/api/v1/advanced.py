"""Evaluation and advanced AI catalog APIs."""

from fastapi import APIRouter, Query

from auth.deps import CurrentUser
from eval.framework import GOLDEN_SET, run_golden_eval, score_agent_performance
from i18n.languages import SUPPORTED_LANGUAGES

router = APIRouter()


@router.get("/advanced-ai")
async def advanced_ai_catalog(user: CurrentUser):
    return {
        "features": [
            "Multi-agent collaboration (Master + specialists)",
            "Hybrid Vector RAG + GraphRAG retrieval",
            "Conversational memory (longitudinal)",
            "Confidence scoring with citations",
            "Human-in-the-loop high-risk review",
            "Explainable AI evidence paths",
            "Voice consultations (STT/TTS)",
            "Multilingual support",
            "FHIR/HL7 EHR interop",
            "Continuous evaluation framework",
        ],
        "languages": SUPPORTED_LANGUAGES,
        "endpoints": {
            "chat": "POST /api/v1/chat",
            "hitl": "GET /api/v1/hitl/reviews",
            "voice_consult": "POST /api/v1/voice/consult",
            "fhir": "GET /api/v1/fhir/metadata",
            "eval": "POST /api/v1/eval/run",
        },
    }


@router.post("/eval/run")
async def eval_run(user: CurrentUser, limit: int = Query(default=3, ge=1, le=10)):
    return await run_golden_eval(limit=limit)


@router.get("/eval/cases")
async def eval_cases(user: CurrentUser):
    return [
        {
            "id": c.id,
            "query": c.query,
            "expect_contains": c.expect_contains,
            "forbid_contains": c.forbid_contains,
            "intent": c.intent,
        }
        for c in GOLDEN_SET
    ]
