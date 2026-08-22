from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, model_validator


class RegisterRequest(BaseModel):
    organization_name: str
    full_name: str
    email: EmailStr | None = None
    phone_number: str
    password: str


class LoginRequest(BaseModel):
    identifier: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    password: str
    otp: str | None = None
    device_id: str | None = None
    device_name: str | None = None

    @model_validator(mode="after")
    def validate_identifier(self) -> "LoginRequest":
        identifiers = [
            value
            for value in (
                self.identifier,
                self.email,
                self.phone_number,
            )
            if value
        ]
        if len(identifiers) != 1:
            raise ValueError("Provide exactly one of identifier, email, or phone_number.")
        return self

    def login_identifier(self) -> str:
        return str(self.identifier or self.email or self.phone_number)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    password: str


class PasswordResetResponse(BaseModel):
    message: str
    reset_token: str | None = None


class MFASetupResponse(BaseModel):
    provisioning_uri: str


class MFAConfirmRequest(BaseModel):
    code: str


class DeviceSessionResponse(BaseModel):
    id: UUID
    device_id: str
    device_name: str | None
    last_ip: str | None
    last_seen_at: datetime
    is_current: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    id: UUID
    organization_id: UUID
    role_id: UUID
    full_name: str
    email: str | None
    phone_number: str
    is_active: bool


class RegisterResponse(BaseModel):
    id: UUID
    organization_id: UUID
    role_id: UUID
    organization_name: str
    role_name: str
    full_name: str
    email: str | None
    phone_number: str


class SendOTPRequest(BaseModel):
    phone_number: str | None = None
    email: EmailStr | None = None


class SendOTPResponse(BaseModel):
    message: str
    test_otp: str | None = None


class VerifyOTPRequest(BaseModel):
    phone_number: str | None = None
    email: EmailStr | None = None
    otp: str


class VerifyOTPResponse(BaseModel):
    verified: bool
    message: str


class GoogleAuthRequest(BaseModel):
    id_token: str
    organization_name: str | None = "My Business"
