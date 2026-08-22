from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ExtractedBillItem(BaseModel):
    description: str | None = None
    quantity: Decimal | None = Field(default=None, ge=0)
    unit: str | None = None
    unit_price: Decimal | None = Field(default=None, ge=0)
    discount_amount: Decimal | None = Field(default=None, ge=0)
    tax_rate: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
    )
    tax_amount: Decimal | None = Field(default=None, ge=0)
    line_total: Decimal | None = Field(default=None, ge=0)
    hsn_code: str | None = None


class ExtractedBill(BaseModel):
    supplier_name: str | None = None
    supplier_gstin: str | None = None

    bill_number: str | None = None
    bill_date: date | None = None
    due_date: date | None = None

    subtotal: Decimal | None = Field(default=None, ge=0)
    discount_amount: Decimal | None = Field(default=None, ge=0)
    taxable_amount: Decimal | None = Field(default=None, ge=0)

    cgst_amount: Decimal | None = Field(default=None, ge=0)
    sgst_amount: Decimal | None = Field(default=None, ge=0)
    igst_amount: Decimal | None = Field(default=None, ge=0)

    total_amount: Decimal | None = Field(default=None, ge=0)

    items: list[ExtractedBillItem] = Field(
        default_factory=list,
    )

    confidence: Decimal | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    warnings: list[str] = Field(
        default_factory=list,
    )