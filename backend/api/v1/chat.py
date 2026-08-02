"""Chat and AI orchestration endpoints."""

from fastapi import APIRouter, Request

from agents.master import get_master_agent
from auth.deps import CurrentUser, DbSession
from hitl.service import HitlService, requires_human_review
from schemas.chat import ChatRequest, ChatResponse
from services.audit_service import AuditService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest, db: DbSession, user: CurrentUser, request: Request):
    master = get_master_agent()
    ctx = data.context or {}
    result = await master.chat(
        data.message,
        conversation_id=data.conversation_id,
        patient_id=data.patient_id,
        language=data.language or ctx.get("language") or "en",
        enable_hitl=data.enable_hitl,
        **ctx,
    )

    review_id = None
    if result.get("human_review") and requires_human_review(
        result.get("risk_level"), result.get("confidence"), result.get("intent")
    ):
        row = await HitlService(db).enqueue(
            conversation_id=result["conversation_id"],
            user_id=user.id,
            draft_reply=result["reply"],
            risk_level=result.get("risk_level"),
            confidence=result.get("confidence"),
            evidence=result.get("citations") or result.get("sources"),
            metadata={"intent": result.get("intent"), "agent": result.get("agent")},
        )
        review_id = row.review_id
        result["human_review"] = {
            "required": True,
            "status": "pending",
            "review_id": review_id,
            "message": "Queued for clinician human-in-the-loop review.",
        }

    await AuditService(db).log(
        "chat",
        "ai",
        user.id,
        data.conversation_id,
        request.client.host if request.client else None,
        details=f"hitl={bool(review_id)}; lang={result.get('language')}",
    )
    result["review_id"] = review_id
    return ChatResponse(**result)
