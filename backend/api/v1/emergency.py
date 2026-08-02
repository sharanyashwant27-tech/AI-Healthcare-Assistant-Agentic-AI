"""Emergency endpoint."""

from fastapi import APIRouter

from agents.master import get_master_agent
from auth.deps import CurrentUser, DbSession
from models.notification import Notification
from schemas.chat import EmergencyRequest, EmergencyResponse

router = APIRouter()


@router.post("/emergency", response_model=EmergencyResponse)
async def emergency(data: EmergencyRequest, db: DbSession, user: CurrentUser):
    master = get_master_agent()
    result = await master.run_named("emergency", data.model_dump())
    if result.get("alert_sent"):
        db.add(
            Notification(
                user_id=user.id,
                channel="push",
                title="Emergency Alert",
                message=result.get("message") or "Emergency detected",
                meta_json=str(result.get("notifications")),
            )
        )
        await db.flush()
    return EmergencyResponse(
        is_emergency=result["is_emergency"],
        emergency_type=result.get("emergency_type"),
        immediate_actions=result["immediate_actions"],
        alert_sent=result["alert_sent"],
        message=result["message"],
    )
