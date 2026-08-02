"""Reminder Agent — medication and care reminders under Master orchestration."""

from typing import Any, Dict, List

from agents.base import BaseAgent
from core.config import settings


class ReminderAgent(BaseAgent):
    name = "reminder"

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        medicine = payload.get("medicine_name") or payload.get("medicine") or "prescribed medication"
        dosage = payload.get("dosage") or "as prescribed"
        schedule = payload.get("schedule") or "08:00,20:00"
        notes = payload.get("notes") or payload.get("message") or ""

        reminders: List[Dict[str, str]] = [
            {
                "type": "medication",
                "title": f"Medication: {medicine}",
                "message": f"Take {medicine} ({dosage}) at {schedule}. {notes}".strip(),
                "schedule": schedule,
            }
        ]
        if payload.get("follow_up_at"):
            reminders.append(
                {
                    "type": "follow_up",
                    "title": "Follow-up reminder",
                    "message": f"Follow-up due around {payload['follow_up_at']}",
                    "schedule": str(payload["follow_up_at"]),
                }
            )

        reply = (
            f"Reminder prepared for {medicine} ({dosage}) at {schedule}. "
            "Confirm and enable notifications from the Reminders module. "
            "Take medicines only as directed by your clinician."
        )
        return {
            "agent": self.name,
            "reminders": reminders,
            "medicine_name": medicine,
            "dosage": dosage,
            "schedule": schedule,
            "reply": reply,
            "disclaimer": settings.medical_disclaimer,
        }
