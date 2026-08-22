from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class OCRCorrectionCreate(BaseModel):
    bill_id: UUID | None = None
    field_name: str = Field(min_length=1, max_length=100)
    ocr_value: str
    final_value: str
    ocr_numeric_value: Decimal | None = None
    final_numeric_value: Decimal | None = None
    context: str | None = None
