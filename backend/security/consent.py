"""Consent management for HIPAA/GDPR-aware data handling."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.consent import ConsentRecord


CONSENT_TYPES = [
    "ai_processing",
    "data_storage",
    "telemedicine",
    "research_deidentified",
    "marketing",
]


class ConsentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def set_consent(
        self,
        user_id: int,
        consent_type: str,
        granted: bool,
        version: str = "1.0",
        meta: Optional[str] = None,
    ) -> ConsentRecord:
        if consent_type not in CONSENT_TYPES:
            raise ValueError(f"Unknown consent_type. Allowed: {', '.join(CONSENT_TYPES)}")
        existing = (
            await self.db.execute(
                select(ConsentRecord).where(
                    ConsentRecord.user_id == user_id,
                    ConsentRecord.consent_type == consent_type,
                )
            )
        ).scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if existing:
            existing.granted = granted
            existing.version = version
            existing.meta_json = meta
            existing.updated_at = now
            await self.db.flush()
            return existing
        row = ConsentRecord(
            user_id=user_id,
            consent_type=consent_type,
            granted=granted,
            version=version,
            meta_json=meta,
            updated_at=now,
        )
        self.db.add(row)
        await self.db.flush()
        return row

    async def list_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        rows = (
            await self.db.execute(
                select(ConsentRecord).where(ConsentRecord.user_id == user_id)
            )
        ).scalars().all()
        by_type = {r.consent_type: r for r in rows}
        out = []
        for ctype in CONSENT_TYPES:
            row = by_type.get(ctype)
            out.append(
                {
                    "consent_type": ctype,
                    "granted": bool(row.granted) if row else False,
                    "version": row.version if row else None,
                    "updated_at": row.updated_at.isoformat() if row and row.updated_at else None,
                }
            )
        return out

    async def has_consent(self, user_id: int, consent_type: str) -> bool:
        row = (
            await self.db.execute(
                select(ConsentRecord).where(
                    ConsentRecord.user_id == user_id,
                    ConsentRecord.consent_type == consent_type,
                    ConsentRecord.granted.is_(True),
                )
            )
        ).scalar_one_or_none()
        return row is not None
