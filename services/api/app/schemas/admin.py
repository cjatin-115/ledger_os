from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RoleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    permission_codes: list[str] = Field(default_factory=list)


class RoleResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    description: str | None
    is_active: bool
    permission_codes: list[str]


class UserCreateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone_number: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=8)
    role_id: UUID


class UserResponse(BaseModel):
    id: UUID
    organization_id: UUID
    role_id: UUID
    full_name: str
    email: str | None
    phone_number: str
    is_active: bool
