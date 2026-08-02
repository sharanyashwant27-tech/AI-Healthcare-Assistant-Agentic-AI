import pytest

from agents.emergency_agent import EmergencyAgent
from agents.nutrition_agent import NutritionAgent
from agents.symptom_agent import SymptomAnalysisAgent


@pytest.mark.asyncio
async def test_emergency_agent_flags_chest_pain():
    agent = EmergencyAgent()
    result = await agent.run({"symptoms": ["chest pain"], "description": "sweating"})
    assert result["is_emergency"] is True
    assert result["alert_sent"] is True


@pytest.mark.asyncio
async def test_nutrition_bmi():
    agent = NutritionAgent()
    result = await agent.run(
        {"age": 30, "gender": "female", "height_cm": 162, "weight_kg": 58, "activity_level": "moderate"}
    )
    assert result["bmi"] > 0
    assert result["daily_calories"] > 1000


@pytest.mark.asyncio
async def test_symptom_agent_uncertainty():
    agent = SymptomAnalysisAgent()
    result = await agent.run({"symptoms": ["fever", "cough"]})
    assert "possible_conditions" in result
    assert result["risk_level"] in {"moderate", "high", "critical", "low"}
