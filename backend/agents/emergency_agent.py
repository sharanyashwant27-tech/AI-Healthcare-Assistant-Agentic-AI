"""Emergency Agent — heart attack/stroke detection, alerts, ambulance workflow."""

from typing import Any, Dict, List

from agents.base import BaseAgent
from core.config import settings
from core.logging import get_logger
from prompts.registry import get_prompt_registry
from utils.llm import generate_text
from workflows.triggers import trigger_n8n_workflow

logger = get_logger(__name__)

EMERGENCY_MAP = {
    "heart attack": ["chest pain", "left arm pain", "crushing chest", "sweating with chest"],
    "stroke": ["face droop", "arm weakness", "slurred speech", "stroke", "sudden numbness"],
    "high fever": ["high fever", "fever 104", "fever 40", "seizure with fever"],
    "respiratory": ["cannot breathe", "difficulty breathing", "blue lips", "severe shortness of breath"],
}


class EmergencyAgent(BaseAgent):
    name = "emergency"

    def __init__(self) -> None:
        self.prompts = get_prompt_registry()

    def classify(self, symptoms: List[str], description: str) -> tuple[bool, str | None]:
        blob = " ".join(symptoms + [description or ""]).lower()
        for etype, keys in EMERGENCY_MAP.items():
            if any(k in blob for k in keys):
                return True, etype
        return False, None

    async def _trigger_workflows(self, payload: Dict[str, Any], etype: str | None) -> Dict[str, Any]:
        result = await trigger_n8n_workflow(
            "emergency",
            {
                "emergency_type": etype,
                "symptoms": payload.get("symptoms"),
                "description": payload.get("description") or payload.get("message"),
                "location": payload.get("location"),
                "patient_id": payload.get("patient_id"),
                "critical": True,
                "actions": [
                    "Symptoms",
                    "Critical Check",
                    "Doctor Alert",
                    "Ambulance",
                    "Hospital",
                    "Family Notification",
                ],
            },
        )
        return {
            "workflow_called": bool(result.get("triggered")),
            **result,
        }

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        symptoms = payload.get("symptoms") or []
        description = payload.get("description") or payload.get("message") or ""
        is_emergency, etype = self.classify(symptoms, description)
        prompt = self.prompts.as_langchain("emergency").format(
            symptoms=", ".join(symptoms) or "n/a",
            description=description,
        )
        narrative = await generate_text(prompt)

        actions = [
            "Call local emergency services immediately",
            "Do not drive yourself if symptoms are severe",
            "Notify an emergency contact / family member",
            "Share location with ambulance dispatch if available",
        ]
        workflow = {"workflow_called": False}
        ambulance = {"booked": False, "status": "not_required"}
        if is_emergency:
            workflow = await self._trigger_workflows(payload, etype)
            ambulance = {
                "booked": True,
                "status": "dispatch_requested",
                "note": "Ambulance booking requested via emergency workflow (confirm with local EMS).",
            }
        else:
            actions = [
                "Monitor symptoms closely",
                "Contact a licensed clinician for guidance",
                "Seek urgent care if symptoms worsen",
            ]

        return {
            "agent": self.name,
            "is_emergency": is_emergency,
            "emergency_type": etype,
            "immediate_actions": actions,
            "alert_sent": is_emergency,
            "ambulance": ambulance,
            "workflow": workflow,
            "notifications": {
                "ambulance": is_emergency,
                "doctor": is_emergency,
                "family": is_emergency,
            },
            "message": narrative,
            "reply": narrative,
            "risk_level": "critical" if is_emergency else "low",
            "disclaimer": settings.medical_disclaimer,
        }
