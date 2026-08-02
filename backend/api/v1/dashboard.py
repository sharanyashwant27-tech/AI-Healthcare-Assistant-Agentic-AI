"""Dashboard endpoint — patient / doctor / admin feature boards."""

from fastapi import APIRouter

from auth.deps import CurrentUser, DbSession
from schemas.patient import DashboardResponse
from services.dashboard_service import build_dashboard

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(db: DbSession, user: CurrentUser):
    payload = await build_dashboard(db, user)
    return DashboardResponse(**payload)
