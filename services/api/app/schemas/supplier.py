from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SupplierCreate(BaseModel):
    """Fields accepted when creating a supplier."""

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    contact_person: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    email: EmailStr | None = None

    gstin: str | None = Field(
        default=None,
        max_length=15,
    )

    address: str | None = None

    payment_terms_days: int | None = Field(
        default=None,
        ge=0,
    )


class SupplierUpdate(BaseModel):
    """Fields accepted when partially updating a supplier."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    contact_person: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    email: EmailStr | None = None

    gstin: str | None = Field(
        default=None,
        max_length=15,
    )

    address: str | None = None

    payment_terms_days: int | None = Field(
        default=None,
        ge=0,
    )

    is_active: bool | None = None


class SupplierResponse(BaseModel):
    """Supplier data returned by the API."""

    id: UUID
    name: str
    contact_person: str | None
    phone: str | None
    email: str | None
    gstin: str | None
    address: str | None
    payment_terms_days: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
