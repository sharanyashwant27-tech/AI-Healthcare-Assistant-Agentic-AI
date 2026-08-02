"""Appointment Agent — doctor/department/time slot with HMS integration hook."""

from datetime import datetime, timezone
from typing import Any, Dict

import httpx

from agents.base import BaseAgent
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

DEPARTMENT_MAP = {
    "internal medicine": "INTMED",
    "cardiology": "CARDIO",
    "neurology": "NEURO",
    "emergency medicine": "ER",
    "general physician": "INTMED",
}


class AppointmentAgent(BaseAgent):
    name = "appointment"

    async def _push_hms(self, booking: Dict[str, Any]) -> Dict[str, Any]:
        """Optional Hospital Management System webhook integration."""
        hms_url = getattr(settings, "hms_webhook_url", "") or ""
        if not hms_url:
            return {"integrated": False, "mode": "internal_calendar"}
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.post(hms_url, json=booking)
                return {"integrated": True, "status_code": resp.status_code, "mode": "hms"}
        except Exception as exc:  # noqa: BLE001
            logger.warning("hms_integration_failed", error=str(exc))
            return {"integrated": False, "mode": "internal_calendar", "error": str(exc)}

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action") or "book"
        doctor_id = payload.get("doctor_id")
        department = payload.get("department") or "Internal Medicine"
        dept_code = DEPARTMENT_MAP.get(department.lower(), "GEN")
        scheduled_at = payload.get("scheduled_at") or payload.get("time_slot")
        reason = payload.get("reason") or payload.get("message")

        if action == "reschedule":
            return {
                "agent": self.name,
                "status": "rescheduled",
                "appointment_id": payload.get("appointment_id"),
                "doctor": doctor_id,
                "department": department,
                "time_slot": scheduled_at,
                "reminder": True,
                "reply": f"Appointment rescheduled to {scheduled_at} in {department}.",
            }

        booking = {
            "doctor_id": doctor_id,
            "department": department,
            "department_code": dept_code,
            "time_slot": scheduled_at or datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "patient_id": payload.get("patient_id"),
        }
        hms = await self._push_hms(booking)

        return {
            "agent": self.name,
            "status": "scheduled" if scheduled_at else "pending_availability",
            "doctor": doctor_id,
            "department": department,
            "department_code": dept_code,
            "time_slot": booking["time_slot"],
            "scheduled_at": booking["time_slot"],
            "reason": reason,
            "calendar": hms.get("mode"),
            "hms": hms,
            "reminder": True,
            "reply": (
                f"Appointment prepared for doctor #{doctor_id} / {department} "
                f"at {booking['time_slot']}. HMS mode: {hms.get('mode')}."
            ),
        }
