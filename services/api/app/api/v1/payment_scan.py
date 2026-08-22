from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_organization_id
from app.db.session import get_db
from app.schemas.payment_extraction import ExtractedPayment, PaymentScanConfirmResponse
from app.services.payment_extraction import PaymentExtractionService


def _money_str(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.quantize(Decimal("0.01")), "f")


router = APIRouter(prefix="/payments", tags=["Payments"])


class PaymentScanRequest(BaseModel):
    raw_text: str


def get_payment_extraction_service(
    db: AsyncSession = Depends(get_db),
) -> PaymentExtractionService:
    return PaymentExtractionService(db)


@router.post("/scan-image")
async def scan_payment_image(
    file: UploadFile = File(...),
    organization_id: UUID = Depends(get_current_organization_id),
    service: PaymentExtractionService = Depends(get_payment_extraction_service),
) -> dict:
    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty image file provided.",
        )
    mime_type = file.content_type or "image/jpeg"
    extracted = await service.extract_from_image(contents, mime_type, organization_id)
    data = extracted.model_dump(mode="json")
    if data.get("amount") is not None:
        data["amount"] = _money_str(Decimal(str(data["amount"])))
    if data.get("confidence") is not None:
        data["confidence"] = float(data["confidence"])
    return data


@router.post("/scan")
async def scan_payment(
    payload: PaymentScanRequest,
    organization_id: UUID = Depends(get_current_organization_id),
    service: PaymentExtractionService = Depends(get_payment_extraction_service),
) -> dict:
    if not payload.raw_text or not payload.raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment receipt text is required.",
        )

    extracted = await service.extract_from_text(payload.raw_text, organization_id)
    data = extracted.model_dump(mode="json")
    if data.get("amount") is not None:
        data["amount"] = _money_str(Decimal(str(data["amount"])))
    if data.get("confidence") is not None:
        data["confidence"] = float(data["confidence"])
    return data


@router.post("/scan/confirm", response_model=PaymentScanConfirmResponse)
async def confirm_payment_scan(
    payload: ExtractedPayment,
    organization_id: UUID = Depends(get_current_organization_id),
    service: PaymentExtractionService = Depends(get_payment_extraction_service),
) -> PaymentScanConfirmResponse:
    try:
        result = await service.confirm_extracted_payment(
            payload=payload,
            organization_id=organization_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return PaymentScanConfirmResponse.model_validate(result)
