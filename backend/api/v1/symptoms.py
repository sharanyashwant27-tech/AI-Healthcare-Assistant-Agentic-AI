"""Symptom analysis endpoint."""

from fastapi import APIRouter

from agents.master import get_master_agent
from auth.deps import CurrentUser
from schemas.chat import SymptomAnalysisRequest, SymptomAnalysisResponse

router = APIRouter()


@router.post("/symptom-analysis", response_model=SymptomAnalysisResponse)
async def symptom_analysis(data: SymptomAnalysisRequest, user: CurrentUser):
    master = get_master_agent()
    result = await master.run_named("symptom", data.model_dump())
    return SymptomAnalysisResponse(
        possible_conditions=result["possible_conditions"],
        risk_level=result["risk_level"],
        risk_score=int(result.get("risk_score") or 50),
        next_action=result.get("next_action"),
        recommended_specialist=result.get("recommended_specialist"),
        urgency=result["urgency"],
        advice=result["advice"],
        emergency_flags=result.get("emergency_flags", []),
    )
