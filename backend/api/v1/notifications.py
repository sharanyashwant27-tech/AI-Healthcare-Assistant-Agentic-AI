"""Notification Center endpoints."""

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from auth.deps import CurrentUser, DbSession
from models.notification import Notification

router = APIRouter()


@router.get("/notifications")
async def list_notifications(db: DbSession, user: CurrentUser, unread_only: bool = False):
    stmt = (
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(100)
    )
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": n.id,
            "channel": n.channel,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in rows
    ]


@router.post("/notifications/{notification_id}/read")
async def mark_read(notification_id: int, db: DbSession, user: CurrentUser):
    row = (
        await db.execute(
            select(Notification).where(
                Notification.id == notification_id, Notification.user_id == user.id
            )
        )
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Notification not found")
    row.is_read = True
    await db.flush()
    return {"id": row.id, "is_read": True}


@router.post("/notifications/read-all")
async def mark_all_read(db: DbSession, user: CurrentUser):
    rows = (
        await db.execute(select(Notification).where(Notification.user_id == user.id))
    ).scalars().all()
    for n in rows:
        n.is_read = True
    await db.flush()
    return {"updated": len(rows)}
