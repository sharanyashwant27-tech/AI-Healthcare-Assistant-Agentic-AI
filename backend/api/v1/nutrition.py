"""Nutrition endpoint."""

from fastapi import APIRouter

from agents.master import get_master_agent
from auth.deps import CurrentUser
from schemas.chat import NutritionRequest, NutritionResponse

router = APIRouter()


@router.post("/nutrition", response_model=NutritionResponse)
async def nutrition_plan(data: NutritionRequest, user: CurrentUser):
    master = get_master_agent()
    result = await master.run_named("nutrition", data.model_dump())
    return NutritionResponse(
        bmi=result["bmi"],
        bmi_category=result["bmi_category"],
        daily_calories=result["daily_calories"],
        water_intake_liters=result["water_intake_liters"],
        diet_plan=result["diet_plan"],
        exercise_plan=result["exercise_plan"],
    )
