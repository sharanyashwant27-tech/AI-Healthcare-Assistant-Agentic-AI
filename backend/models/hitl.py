"""HITL review queue model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class HitlReview(Base):
    __tablename__ = "hitl_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    conversation_id: Mapped[str] = mapped_column(String(64), index=True)
    requester_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    reviewer_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    risk_level: Mapped[str] = mapped_column(String(40), default="unknown")
    confidence_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    draft_reply: Mapped[str] = mapped_column(Text)
    final_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
