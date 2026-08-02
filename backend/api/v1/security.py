"""Security and compliance APIs."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select

from auth.deps import CurrentUser, DbSession, require_roles
from models.audit import AuditLog
from models.user import User
from security.consent import CONSENT_TYPES, ConsentService
from security.encryption import encryption_status
from security.phi import mask_phi_with_report
from security.secrets import secrets_status
from services.audit_service import AuditService

router = APIRouter()


class ConsentUpdate(BaseModel):
    consent_type: str = Field(..., description=f"One of: {', '.join(CONSENT_TYPES)}")
    granted: bool = True
    version: str = "1.0"


class PhiMaskRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)


@router.get("/security")
async def security_overview(user: CurrentUser):
    return {
        "jwt_authentication": True,
        "rbac": True,
        "audit_logging": True,
        "data_encryption": encryption_status(),
        "tls_https": {
            "local_dev": "HTTP on localhost — terminate TLS via reverse proxy in production",
            "nginx_sample": "docker/nginx.conf",
        },
        "secrets_management": secrets_status(),
        "hipaa_gdpr_aware": True,
        "consent_management": True,
        "phi_masking_in_ai_prompts": True,
        "roles": user.role_names,
    }


@router.get("/consent")
async def get_consents(db: DbSession, user: CurrentUser):
    return {"consents": await ConsentService(db).list_for_user(user.id), "types": CONSENT_TYPES}


@router.post("/consent")
async def update_consent(data: ConsentUpdate, db: DbSession, user: CurrentUser):
    try:
        row = await ConsentService(db).set_consent(
            user.id, data.consent_type, data.granted, data.version
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await AuditService(db).log(
        "consent_update",
        "consent",
        user.id,
        data.consent_type,
        details=f"granted={data.granted}",
    )
    return {
        "consent_type": row.consent_type,
        "granted": row.granted,
        "version": row.version,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


@router.post("/security/mask-phi")
async def preview_phi_mask(data: PhiMaskRequest, user: CurrentUser):
    masked, report = mask_phi_with_report(data.text)
    return {"masked": masked, "redactions": report}


@router.get("/security/audit")
async def list_audit(
    db: DbSession,
    user: User = Depends(require_roles("admin")),
    limit: int = Query(default=50, ge=1, le=200),
):
    rows = (
        await db.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        )
    ).scalars().all()
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "action": r.action,
            "resource": r.resource,
            "resource_id": r.resource_id,
            "ip_address": r.ip_address,
            "details": r.details,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
