"""Insurance endpoint."""

from fastapi import APIRouter

from agents.master import get_master_agent
from auth.deps import CurrentUser
from schemas.chat import InsuranceRequest, InsuranceResponse

router = APIRouter()


@router.post("/insurance", response_model=InsuranceResponse)
async def validate_insurance(data: InsuranceRequest, user: CurrentUser):
    master = get_master_agent()
    result = await master.run_named("insurance", data.model_dump())
    return InsuranceResponse(
        is_valid=result["is_valid"],
        coverage_summary=result["coverage_summary"],
        claim_eligible=result["claim_eligible"],
        network_status=result["network_status"],
        details=result.get("details", {}),
    )
