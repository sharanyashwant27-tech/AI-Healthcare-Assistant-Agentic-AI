"""Medical Knowledge Assistant endpoint — hybrid RAG + GraphRAG."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agents.master import get_master_agent
from auth.deps import CurrentUser
from schemas.common import MedicalDisclaimerMixin

router = APIRouter()


class KnowledgeRequest(BaseModel):
    query: str = Field(min_length=2, max_length=4000)
    use_graph: bool = True
    language: str = "en"


class KnowledgeResponse(MedicalDisclaimerMixin):
    answer: str
    sources: list = []
    citations: List[Dict[str, Any]] = []
    confidence: Optional[Dict[str, Any]] = None
    explanation: Optional[Dict[str, Any]] = None
    graph_entities: list = []
    agent: str = "medical_knowledge"
    mode: str = "hybrid"


@router.post("/knowledge", response_model=KnowledgeResponse)
async def medical_knowledge(data: KnowledgeRequest, user: CurrentUser):
    master = get_master_agent()
    result = await master.run_named(
        "knowledge",
        {
            "message": data.query,
            "query": data.query,
            "use_graph": data.use_graph,
            "language": data.language,
        },
    )
    return KnowledgeResponse(
        answer=result.get("reply") or result.get("answer") or "",
        sources=result.get("sources") or [],
        citations=result.get("citations") or [],
        confidence=result.get("confidence"),
        explanation=result.get("explanation"),
        graph_entities=result.get("graph_entities") or [],
        mode=result.get("mode") or "hybrid",
    )
