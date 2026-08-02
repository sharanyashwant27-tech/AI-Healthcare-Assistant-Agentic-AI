"""Role-aware dashboard assembly."""

from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.appointment import Appointment
from models.doctor import Doctor
from models.hospital import Hospital
from models.medicine import Prescription
from models.notification import Notification
from models.patient import Patient
from models.report import LabReport
from models.user import User
from security.consent import ConsentService


async def build_dashboard(db: AsyncSession, user: User) -> Dict[str, Any]:
    roles = user.role_names
    role = "admin" if "admin" in roles else (roles[0] if roles else "patient")

    notes = (
        await db.execute(
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .limit(8)
        )
    ).scalars().all()

    if role == "patient":
        return await _patient_dashboard(db, user, notes)
    if role == "doctor":
        return await _doctor_dashboard(db, user, notes)
    return await _admin_dashboard(db, user, notes)


async def _patient_dashboard(db: AsyncSession, user: User, notes: List[Notification]) -> Dict[str, Any]:
    patient = (
        await db.execute(select(Patient).where(Patient.user_id == user.id))
    ).scalar_one_or_none()

    appts: List[Appointment] = []
    prescriptions: List[Prescription] = []
    reports: List[LabReport] = []
    reminders = [n for n in notes if n.channel == "reminder"]

    if patient:
        appts = (
            await db.execute(
                select(Appointment)
                .where(Appointment.patient_id == patient.id)
                .order_by(Appointment.scheduled_at.desc())
                .limit(5)
            )
        ).scalars().all()
        prescriptions = (
            await db.execute(
                select(Prescription)
                .where(Prescription.patient_id == patient.id)
                .order_by(Prescription.created_at.desc())
                .limit(5)
            )
        ).scalars().all()
        reports = (
            await db.execute(
                select(LabReport)
                .where(LabReport.patient_id == patient.id)
                .order_by(LabReport.created_at.desc())
                .limit(5)
            )
        ).scalars().all()

    consents = await ConsentService(db).list_for_user(user.id)
    health_summary = {
        "blood_group": patient.blood_group if patient else None,
        "allergies": patient.allergies if patient else None,
        "height_cm": patient.height_cm if patient else None,
        "weight_kg": patient.weight_kg if patient else None,
        "gender": patient.gender if patient else None,
    }

    return {
        "role": "patient",
        "features": [
            "Health summary",
            "Appointments",
            "Prescriptions",
            "Reports",
            "AI Chat",
            "Medication reminders",
        ],
        "stats": {
            "appointments": len(appts),
            "prescriptions": len(prescriptions),
            "reports": len(reports),
            "reminders": len(reminders),
            "unread_notifications": sum(1 for n in notes if not n.is_read),
        },
        "health_summary": health_summary,
        "appointments": [
            {
                "id": a.id,
                "doctor_id": a.doctor_id,
                "scheduled_at": a.scheduled_at.isoformat(),
                "status": a.status,
                "reason": a.reason,
            }
            for a in appts
        ],
        "prescriptions": [
            {
                "id": p.id,
                "dosage": p.dosage,
                "duration": p.duration,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in prescriptions
        ],
        "reports": [
            {
                "id": r.id,
                "report_type": r.report_type,
                "summary": r.summary,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reports
        ],
        "reminders": [
            {"id": n.id, "title": n.title, "message": n.message, "is_read": n.is_read}
            for n in reminders
        ],
        "ai_chat": {"enabled": True, "href": "/chat"},
        "recent_appointments": [
            {
                "id": a.id,
                "doctor_id": a.doctor_id,
                "patient_id": a.patient_id,
                "scheduled_at": a.scheduled_at.isoformat(),
                "status": a.status,
            }
            for a in appts
        ],
        "notifications": [
            {"id": n.id, "title": n.title, "message": n.message, "is_read": n.is_read}
            for n in notes
        ],
        "consents": consents,
        "alerts": [
            "AI outputs are informational only — not a diagnosis.",
            "Escalate emergencies to local emergency services immediately.",
        ],
    }


async def _doctor_dashboard(db: AsyncSession, user: User, notes: List[Notification]) -> Dict[str, Any]:
    doctor = (
        await db.execute(select(Doctor).where(Doctor.user_id == user.id))
    ).scalar_one_or_none()

    queue_q = select(Appointment).order_by(Appointment.scheduled_at.asc()).limit(10)
    if doctor:
        queue_q = (
            select(Appointment)
            .where(Appointment.doctor_id == doctor.id)
            .order_by(Appointment.scheduled_at.asc())
            .limit(10)
        )
    queue = (await db.execute(queue_q)).scalars().all()

    patients_count = (await db.execute(select(func.count()).select_from(Patient))).scalar() or 0
    labs = (
        await db.execute(select(LabReport).order_by(LabReport.created_at.desc()).limit(5))
    ).scalars().all()

    risk_alerts = [
        n for n in notes if n.channel in {"emergency", "alert", "risk"} or "risk" in (n.title or "").lower()
    ]
    if not risk_alerts:
        risk_alerts_payload = [
            {"level": "info", "message": "No critical risk alerts in notification feed."}
        ]
    else:
        risk_alerts_payload = [
            {"level": "high", "message": f"{n.title}: {n.message}"} for n in risk_alerts[:5]
        ]

    return {
        "role": "doctor",
        "features": [
            "Patient queue",
            "AI summaries",
            "Risk alerts",
            "Lab insights",
            "Clinical notes",
        ],
        "stats": {
            "queue": len(queue),
            "patients": patients_count,
            "lab_insights": len(labs),
            "risk_alerts": len(risk_alerts_payload),
        },
        "patient_queue": [
            {
                "appointment_id": a.id,
                "patient_id": a.patient_id,
                "scheduled_at": a.scheduled_at.isoformat(),
                "status": a.status,
                "reason": a.reason,
            }
            for a in queue
        ],
        "ai_summaries": [
            {
                "title": "Visit support",
                "summary": "Use Knowledge / Chat for guideline-backed differentials — never diagnose with certainty.",
            },
            {
                "title": "Lab assist",
                "summary": "Review flagged lab values in Lab insights before changing therapy.",
            },
        ],
        "risk_alerts": risk_alerts_payload,
        "lab_insights": [
            {
                "id": r.id,
                "patient_id": r.patient_id,
                "report_type": r.report_type,
                "summary": r.summary,
                "abnormalities": r.abnormalities,
            }
            for r in labs
        ],
        "clinical_notes": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notes
            if n.channel in {"clinical", "note", "in_app", "reminder"}
        ][:5]
        or [
            {
                "id": 0,
                "title": "Clinical notes",
                "message": "Add follow-up notes from Follow-up / Chat workflows.",
                "created_at": None,
            }
        ],
        "recent_appointments": [
            {
                "id": a.id,
                "doctor_id": a.doctor_id,
                "patient_id": a.patient_id,
                "scheduled_at": a.scheduled_at.isoformat(),
                "status": a.status,
            }
            for a in queue
        ],
        "notifications": [
            {"id": n.id, "title": n.title, "message": n.message, "is_read": n.is_read}
            for n in notes
        ],
        "alerts": [
            "Review risk alerts before discharging high-acuity patients.",
            "AI summaries are decision support only.",
        ],
    }


async def _admin_dashboard(db: AsyncSession, user: User, notes: List[Notification]) -> Dict[str, Any]:
    patients_count = (await db.execute(select(func.count()).select_from(Patient))).scalar() or 0
    doctors_count = (await db.execute(select(func.count()).select_from(Doctor))).scalar() or 0
    appts_count = (await db.execute(select(func.count()).select_from(Appointment))).scalar() or 0
    users_count = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    hospitals_count = (await db.execute(select(func.count()).select_from(Hospital))).scalar() or 0
    labs_count = (await db.execute(select(func.count()).select_from(LabReport))).scalar() or 0
    rx_count = (await db.execute(select(func.count()).select_from(Prescription))).scalar() or 0

    by_status = (
        await db.execute(
            select(Appointment.status, func.count())
            .group_by(Appointment.status)
        )
    ).all()

    recent = (
        await db.execute(select(Appointment).order_by(Appointment.scheduled_at.desc()).limit(5))
    ).scalars().all()

    return {
        "role": "admin",
        "features": [
            "Hospital analytics",
            "AI usage",
            "Appointment statistics",
            "Operational metrics",
        ],
        "stats": {
            "patients": patients_count,
            "doctors": doctors_count,
            "appointments": appts_count,
            "users": users_count,
            "hospitals": hospitals_count,
        },
        "hospital_analytics": {
            "hospitals": hospitals_count,
            "doctors": doctors_count,
            "patients": patients_count,
            "lab_reports": labs_count,
            "prescriptions": rx_count,
        },
        "ai_usage": {
            "modules": [
                "chat",
                "symptom-analysis",
                "prescription",
                "lab-report",
                "knowledge",
                "embeddings",
            ],
            "note": "Track provider tokens via your LLM vendor dashboards; local offline mode uses no external tokens.",
        },
        "appointment_statistics": {
            "total": appts_count,
            "by_status": {str(status): int(count) for status, count in by_status},
        },
        "operational_metrics": {
            "active_users": users_count,
            "notifications_open": sum(1 for n in notes if not n.is_read),
            "services": ["api", "rag", "graphrag", "n8n", "vector_db"],
        },
        "recent_appointments": [
            {
                "id": a.id,
                "doctor_id": a.doctor_id,
                "patient_id": a.patient_id,
                "scheduled_at": a.scheduled_at.isoformat(),
                "status": a.status,
            }
            for a in recent
        ],
        "notifications": [
            {"id": n.id, "title": n.title, "message": n.message, "is_read": n.is_read}
            for n in notes
        ],
        "alerts": [
            "Enforce TLS/HTTPS and rotate secrets in production.",
            "Review audit logs for privileged access.",
        ],
    }
