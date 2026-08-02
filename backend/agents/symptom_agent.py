"""Symptom Analysis Agent."""

from typing import Any, Dict, List

from agents.base import BaseAgent
from core.config import settings
from graphrag.neo4j_client import get_graph_service
from prompts.builder import build_prompt
from utils.llm import generate_text

EMERGENCY_KEYWORDS = {
    "chest pain",
    "crushing chest",
    "stroke",
    "face droop",
    "slurred speech",
    "cannot breathe",
    "difficulty breathing",
    "severe bleeding",
    "unconscious",
    "suicidal",
}

RISK_SCORES = {"low": 25, "moderate": 50, "high": 75, "critical": 95}


class SymptomAnalysisAgent(BaseAgent):
    name = "symptom_analysis"

    def __init__(self) -> None:
        self.graph = get_graph_service()

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        symptoms: List[str] = payload.get("symptoms") or []
        if payload.get("message") and not symptoms:
            symptoms = [s.strip() for s in payload["message"].replace(",", " ").split() if len(s) > 3]

        age = payload.get("age")
        gender = payload.get("gender")
        medical_history = (
            payload.get("medical_history")
            or payload.get("history")
            or payload.get("additional_notes")
            or ""
        )
        current_medicines = payload.get("current_medicines") or payload.get("medicines") or "none reported"
        allergies = payload.get("allergies") or "none reported"

        emergency_flags = [
            kw for kw in EMERGENCY_KEYWORDS if any(kw in s.lower() for s in symptoms)
        ] + [
            kw
            for kw in EMERGENCY_KEYWORDS
            if kw in (payload.get("message") or "").lower()
            or kw in str(medical_history).lower()
        ]
        emergency_flags = sorted(set(emergency_flags))

        graph_diseases = self.graph.query_symptoms_to_diseases(symptoms)
        context = (
            "Knowledge graph disease associations: "
            + ", ".join(
                str(d.get("disease") or d.get("name") or d) for d in graph_diseases[:5]
            )
            if graph_diseases
            else "No graph matches; rely on general guidelines and uncertainty."
        )
        prompt = build_prompt(
            "symptom",
            {
                "symptoms": ", ".join(symptoms) or "n/a",
                "age": age or "unknown",
                "gender": gender or "unknown",
                "medical_history": str(medical_history) or "none reported",
                "current_medicines": str(current_medicines),
                "allergies": str(allergies),
                "duration": payload.get("duration") or "unknown",
                "severity": payload.get("severity") or "unknown",
                "context": context,
            },
            dynamic_payload={
                "patient_type": payload.get("patient_type") or "patient",
                "age": age,
                "disease": payload.get("disease") or payload.get("known_condition"),
                "country": payload.get("country"),
                "hospital_protocol": payload.get("hospital_protocol"),
            },
            include_few_shot=True,
        )
        advice = await generate_text(prompt)

        possible = []
        for d in graph_diseases[:5]:
            name = d.get("disease") or d.get("name") or str(d)
            possible.append(
                {
                    "condition": name,
                    "likelihood": "medium",
                    "rationale": "Associated via knowledge graph symptom relationships",
                }
            )
        if not possible:
            possible = [
                {
                    "condition": "Non-specific presentation",
                    "likelihood": "low",
                    "rationale": "Insufficient distinctive pattern; clinical evaluation needed",
                }
            ]

        risk_level = (
            "critical"
            if emergency_flags
            else ("high" if payload.get("severity") == "severe" else "moderate")
        )
        risk_score = RISK_SCORES[risk_level]
        if age and int(age) >= 65 and risk_score < 95:
            risk_score = min(95, risk_score + 10)
            if risk_level == "moderate":
                risk_level = "high"

        urgency = "emergency" if emergency_flags else ("soon" if risk_level == "high" else "routine")
        specialist = "Emergency Medicine" if emergency_flags else "General Physician / Internal Medicine"
        next_action = (
            "Call emergency services immediately"
            if emergency_flags
            else (
                "Book urgent clinician visit / telemedicine today"
                if risk_level == "high"
                else "Schedule routine consultation and monitor symptoms"
            )
        )

        return {
            "agent": self.name,
            "inputs": {
                "symptoms": symptoms,
                "age": age,
                "gender": gender,
                "medical_history": medical_history,
                "current_medicines": current_medicines,
                "allergies": allergies,
            },
            "possible_conditions": possible,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "next_action": next_action,
            "recommended_specialist": specialist,
            "hospital_department": specialist,
            "urgency": urgency,
            "advice": advice,
            "emergency_flags": emergency_flags,
            "disclaimer": settings.medical_disclaimer,
            "reply": f"{advice}\n\nNext action: {next_action} (risk score {risk_score}/100).",
        }
