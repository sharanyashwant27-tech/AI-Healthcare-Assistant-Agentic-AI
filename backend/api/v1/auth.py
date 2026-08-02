"""Auth endpoints."""

from fastapi import APIRouter, HTTPException, Request, status

from auth.deps import CurrentUser, DbSession
from schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from services.audit_service import AuditService
from services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: DbSession, request: Request):
    service = AuthService(db)
    try:
        user = await service.register(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    await AuditService(db).log("register", "user", user.id, str(user.id), request.client.host if request.client else None)
    if "patient" in (user.roles or []):
        from workflows.triggers import trigger_n8n_workflow

        await trigger_n8n_workflow(
            "patient-registration",
            {
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
                "user_id": user.id,
                "role": "patient",
            },
        )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: DbSession, request: Request):
    service = AuthService(db)
    try:
        tokens = await service.login(data)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    await AuditService(db).log("login", "user", None, data.email, request.client.host if request.client else None)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: DbSession):
    service = AuthService(db)
    try:
        return await service.refresh(data.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser):
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        roles=user.role_names,
        is_active=user.is_active,
    )
