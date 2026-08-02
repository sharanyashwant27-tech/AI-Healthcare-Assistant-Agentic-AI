"""Nutrition Agent — diet plan, calories, water, BMI, exercise."""

from typing import Any, Dict, List

from agents.base import BaseAgent
from core.config import settings
from prompts.registry import get_prompt_registry
from utils.llm import generate_text


class NutritionAgent(BaseAgent):
    name = "nutrition"

    def __init__(self) -> None:
        self.prompts = get_prompt_registry()

    def bmi(self, height_cm: float, weight_kg: float) -> tuple[float, str]:
        h = height_cm / 100.0
        value = round(weight_kg / (h * h), 1)
        if value < 18.5:
            cat = "underweight"
        elif value < 25:
            cat = "normal"
        elif value < 30:
            cat = "overweight"
        else:
            cat = "obese"
        return value, cat

    def calories(self, weight_kg: float, height_cm: float, age: int, gender: str, activity: str) -> int:
        if gender.lower().startswith("m"):
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        factors = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }
        return int(bmr * factors.get(activity, 1.55))

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        age = int(payload.get("age") or 30)
        gender = payload.get("gender") or "female"
        height = float(payload.get("height_cm") or 165)
        weight = float(payload.get("weight_kg") or 65)
        activity = payload.get("activity_level") or "moderate"
        bmi_val, bmi_cat = self.bmi(height, weight)
        cals = self.calories(weight, height, age, gender, activity)
        water = round(weight * 0.033, 1)
        diet = {
            "breakfast": "Oats / eggs / fruit",
            "lunch": "Lean protein + vegetables + whole grains",
            "dinner": "Light protein + salad + complex carbs",
            "snacks": "Nuts, yogurt, fruit",
            "calories_target": cals,
        }
        exercise: List[str] = [
            "150 minutes moderate aerobic activity weekly",
            "2 strength sessions weekly",
            "Daily walking 30 minutes",
        ]
        prompt = self.prompts.as_langchain("nutrition").format(
            age=age,
            gender=gender,
            height_cm=height,
            weight_kg=weight,
            activity_level=activity,
            goals=payload.get("goals") or "general wellness",
            restrictions=", ".join(payload.get("dietary_restrictions") or []) or "none",
        )
        narrative = await generate_text(prompt)
        return {
            "agent": self.name,
            "bmi": bmi_val,
            "bmi_category": bmi_cat,
            "daily_calories": cals,
            "calories": cals,
            "water_intake_liters": water,
            "diet_plan": diet,
            "exercise_plan": exercise,
            "exercise": exercise,
            "reply": narrative,
            "disclaimer": settings.medical_disclaimer,
        }
