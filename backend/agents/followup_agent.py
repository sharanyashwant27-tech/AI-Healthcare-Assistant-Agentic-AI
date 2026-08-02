"""Follow-up Agent — schedules follow-ups, tests, and notifications."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from agents.base import BaseAgent
from core.config import settings


class FollowUpAgent(BaseAgent):
    name = "followup"

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        reason = payload.get("reason") or payload.get("message") or "clinical follow-up"
        days = int(payload.get("days") or 7)
        tests: List[str] = payload.get("tests") or []
        if not tests and "test" in reason.lower():
            tests = ["Follow-up labs as advised by clinician"]

        follow_up_at = (
            datetime.now(timezone.utc) + timedelta(days=days)
        ).isoformat()
        notifications = [
            {
                "channel": "in_app",
                "title": "Follow-up scheduled",
                "message": f"Follow-up for '{reason}' suggested around {follow_up_at}",
            },
            {
                "channel": "reminder",
                "title": "Follow-up reminder",
                "message": "Please confirm the follow-up visit with your care team.",
            },
        ]
        if tests:
            notifications.append(
                {
                    "channel": "in_app",
                    "title": "Tests recommended",
                    "message": f"Discuss these tests with your clinician: {', '.join(tests)}",
                }
            )

        plan = {
            "follow_up_at": follow_up_at,
            "days": days,
            "reason": reason,
            "recommended_tests": tests,
            "notifications": notifications,
            "next_actions": [
                "Confirm follow-up slot with appointment desk / telemedicine",
                "Complete recommended tests if ordered by a clinician",
                "Bring prior reports and medication list to the visit",
            ],
        }
        reply = (
            f"Follow-up plan prepared in ~{days} days for: {reason}. "
            f"Suggested timing: {follow_up_at}. "
            "This is a scheduling suggestion — confirm with your licensed care team."
        )
        return {
            "agent": self.name,
            "plan": plan,
            "reply": reply,
            "disclaimer": settings.medical_disclaimer,
        }
