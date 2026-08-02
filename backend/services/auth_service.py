"""Authentication service."""

from sqlalchemy.ext.asyncio import AsyncSession

from auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from models.doctor import Doctor
from models.patient import Patient
from models.user import User
from repositories.user_repository import UserRepository
from schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    async def register(self, data: RegisterRequest) -> UserResponse:
        existing = await self.users.get_by_email(data.email.lower())
        if existing:
            raise ValueError("Email already registered")

        role = await self.users.get_or_create_role(data.role)
        user = User(
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            is_active=True,
            is_verified=True,
            roles=[role],
        )
        user = await self.users.create(user)

        if data.role == "patient":
            self.db.add(Patient(user_id=user.id))
        elif data.role == "doctor":
            self.db.add(
                Doctor(
                    user_id=user.id,
                    specialty=data.specialty or "General Medicine",
                    license_number=data.license_number or f"LIC-{user.id:06d}",
                    hospital_name="City General Hospital",
                )
            )
        await self.db.flush()
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            roles=user.role_names,
            is_active=user.is_active,
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.users.get_by_email(data.email.lower())
        if not user or not verify_password(data.password, user.hashed_password):
            raise ValueError("Invalid email or password")
        roles = user.role_names
        return TokenResponse(
            access_token=create_access_token(str(user.id), roles),
            refresh_token=create_refresh_token(str(user.id)),
            roles=roles,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        user = await self.users.get_by_id(int(payload["sub"]))
        if not user:
            raise ValueError("User not found")
        roles = user.role_names
        return TokenResponse(
            access_token=create_access_token(str(user.id), roles),
            refresh_token=create_refresh_token(str(user.id)),
            roles=roles,
        )
