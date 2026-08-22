from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class BillItemCreate(BaseModel):
    """Input for one line item on a supplier bill."""

    description: str = Field(
        min_length=1,
        max_length=500,
    )

    quantity: Decimal = Field(
        gt=0,
        decimal_places=3,
    )

    unit: str = Field(
        default="PCS",
        min_length=1,
        max_length=20,
    )

    unit_price: Decimal = Field(
        ge=0,
        decimal_places=2,
    )

    discount_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
    )

    tax_rate: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
        decimal_places=2,
    )

    tax_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
    )

    line_total: Decimal = Field(
        ge=0,
        decimal_places=2,
    )

    hsn_code: str | None = Field(
        default=None,
        max_length=20,
    )


class BillCreate(BaseModel):
    """Input for creating a supplier bill."""

    supplier_id: UUID

    bill_number: str = Field(
        min_length=1,
        max_length=100,
    )

    bill_date: date

    due_date: date | None = None

    subtotal: Decimal = Field(
        ge=0,
        decimal_places=2,
    )

    discount_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
    )

    taxable_amount: Decimal = Field(
        ge=0,
        decimal_places=2,
    )

    cgst_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
    )

    sgst_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
    )

    igst_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
    )

    total_amount: Decimal = Field(
        ge=0,
        decimal_places=2,
    )

    notes: str | None = None

    items: list[BillItemCreate] = Field(
        default_factory=list,
    )

    @model_validator(mode="after")
    def validate_calculations(self) -> "BillCreate":
        expected_total = self.taxable_amount + self.cgst_amount + self.sgst_amount + self.igst_amount
        if abs(expected_total - self.total_amount) > Decimal("1.00"):
            raise ValueError("Total amount does not match taxes and taxable amount.")
        return self


class BillItemResponse(BaseModel):
    """Bill line item returned by the API."""

    id: UUID
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    discount_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    line_total: Decimal
    hsn_code: str | None

    model_config = {
        "from_attributes": True,
    }


class BillResponse(BaseModel):
    """Bill returned by the API."""

    id: UUID
    organization_id: UUID
    supplier_id: UUID
    supplier_name: str | None = None
    bill_number: str
    bill_date: date
    due_date: date | None
    subtotal: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_amount: Decimal
    status: str
    source_type: str
    notes: str | None
    items: list[BillItemResponse]

    model_config = {
        "from_attributes": True,
    }
