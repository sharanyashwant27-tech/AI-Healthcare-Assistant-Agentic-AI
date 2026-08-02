"""Human-in-the-loop review APIs."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth.deps import CurrentUser, DbSession, require_roles
from hitl.service import HitlService
from models.user import User

router = APIRouter()


class HitlDecision(BaseModel):
    decision: str = Field(..., description="approved | rejected | edited")
    notes: Optional[str] = None
    final_reply: Optional[str] = None


@router.get("/hitl/reviews")
async def list_reviews(
    db: DbSession,
    user: User = Depends(require_roles("doctor", "admin")),
):
    rows = await HitlService(db).list_pending()
    return [
        {
            "review_id": r.review_id,
            "conversation_id": r.conversation_id,
            "risk_level": r.risk_level,
            "status": r.status,
            "draft_reply": r.draft_reply,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.post("/hitl/reviews/{review_id}/decision")
async def decide_review(
    review_id: str,
    data: HitlDecision,
    db: DbSession,
    user: User = Depends(require_roles("doctor", "admin")),
):
    try:
        row = await HitlService(db).decide(
            review_id,
            reviewer_user_id=user.id,
            decision=data.decision,
            notes=data.notes,
            final_reply=data.final_reply,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Review not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "review_id": row.review_id,
        "status": row.status,
        "final_reply": row.final_reply,
        "reviewed_at": row.reviewed_at.isoformat() if row.reviewed_at else None,
    }
