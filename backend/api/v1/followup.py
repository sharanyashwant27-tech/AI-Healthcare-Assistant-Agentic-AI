"""Follow-up Agent API."""

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agents.master import get_master_agent
from auth.deps import CurrentUser, DbSession
from models.notification import Notification
from schemas.common import MedicalDisclaimerMixin

router = APIRouter()


class FollowUpRequest(BaseModel):
    reason: str = Field(min_length=2, max_length=500)
    days: int = Field(default=7, ge=1, le=180)
    tests: Optional[List[str]] = None


class FollowUpResponse(MedicalDisclaimerMixin):
    plan: dict
    reply: str


@router.post("/follow-up", response_model=FollowUpResponse)
async def create_follow_up(data: FollowUpRequest, db: DbSession, user: CurrentUser):
    master = get_master_agent()
    result = await master.run_named("followup", data.model_dump())
    for note in result.get("plan", {}).get("notifications", []):
        db.add(
            Notification(
                user_id=user.id,
                channel=note.get("channel", "in_app"),
                title=note.get("title", "Follow-up"),
                message=note.get("message", ""),
            )
        )
    await db.flush()
    return FollowUpResponse(plan=result["plan"], reply=result["reply"])
