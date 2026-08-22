from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_organization_id,
    get_current_user_id,
    require_permission,
)
from app.db.models.ocr_feedback import OCRCorrectionFeedback
from app.db.session import get_db
from app.schemas.ocr_feedback import OCRCorrectionCreate

router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post("/feedback", status_code=201)
async def create_ocr_feedback(
    payload: OCRCorrectionCreate,
    organization_id: UUID = Depends(get_current_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("bills.write")),
) -> dict[str, str]:
    if payload.bill_id is not None:
        from app.db.models.bill import Bill

        bill = await db.scalar(
            select(Bill).where(
                Bill.id == payload.bill_id,
                Bill.organization_id == organization_id,
            )
        )
        if bill is None:
            raise HTTPException(status_code=404, detail="Bill not found.")

    db.add(
        OCRCorrectionFeedback(
            organization_id=organization_id,
            bill_id=payload.bill_id,
            corrected_by=user_id,
            field_name=payload.field_name.strip(),
            ocr_value=payload.ocr_value,
            final_value=payload.final_value,
            ocr_numeric_value=payload.ocr_numeric_value,
            final_numeric_value=payload.final_numeric_value,
            context=payload.context,
        )
    )
    await db.commit()
    return {"status": "recorded"}
