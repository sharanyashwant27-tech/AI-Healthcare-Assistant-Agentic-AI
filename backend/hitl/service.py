"""Human-in-the-loop review for high-risk AI recommendations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.hitl import HitlReview

HIGH_RISK_LEVELS = {"critical", "high"}


def requires_human_review(
    risk_level: Optional[str],
    confidence: Optional[Dict[str, Any]] = None,
    intent: Optional[str] = None,
) -> bool:
    if risk_level and risk_level.lower() in HIGH_RISK_LEVELS:
        return True
    if intent == "emergency":
        return True
    if confidence and confidence.get("label") == "low" and risk_level in {"moderate", "high", "critical"}:
        return True
    return False


class HitlService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def enqueue(
        self,
        *,
        conversation_id: str,
        user_id: Optional[int],
        draft_reply: str,
        risk_level: Optional[str],
        confidence: Optional[Dict[str, Any]],
        evidence: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> HitlReview:
        import json

        row = HitlReview(
            review_id=str(uuid4()),
            conversation_id=conversation_id,
            requester_user_id=user_id,
            status="pending",
            risk_level=risk_level or "unknown",
            confidence_json=json.dumps(confidence or {}),
            draft_reply=draft_reply,
            evidence_json=json.dumps(evidence or []),
            meta_json=json.dumps(metadata or {}),
        )
        self.db.add(row)
        await self.db.flush()
        return row

    async def list_pending(self, limit: int = 50) -> List[HitlReview]:
        rows = (
            await self.db.execute(
                select(HitlReview)
                .where(HitlReview.status == "pending")
                .order_by(HitlReview.created_at.desc())
                .limit(limit)
            )
        ).scalars().all()
        return list(rows)

    async def decide(
        self,
        review_id: str,
        *,
        reviewer_user_id: int,
        decision: str,
        notes: Optional[str] = None,
        final_reply: Optional[str] = None,
    ) -> HitlReview:
        if decision not in {"approved", "rejected", "edited"}:
            raise ValueError("decision must be approved|rejected|edited")
        row = (
            await self.db.execute(select(HitlReview).where(HitlReview.review_id == review_id))
        ).scalar_one_or_none()
        if not row:
            raise KeyError("review not found")
        row.status = decision
        row.reviewer_user_id = reviewer_user_id
        row.reviewer_notes = notes
        if final_reply:
            row.final_reply = final_reply
        elif decision == "approved":
            row.final_reply = row.draft_reply
        row.reviewed_at = datetime.now(timezone.utc)
        await self.db.flush()
        return row
