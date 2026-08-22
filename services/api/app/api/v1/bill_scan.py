from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_organization_id
from app.db.session import get_db
from app.schemas.bill import BillResponse
from app.schemas.bill_extraction import ExtractedBill
from app.services.bill_extraction import BillExtractionService


def _money_str(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.quantize(Decimal("0.01")), "f")


def _normalize_extracted_payload(payload: dict) -> dict:
    for field in (
        "subtotal",
        "discount_amount",
        "taxable_amount",
        "cgst_amount",
        "sgst_amount",
        "igst_amount",
        "total_amount",
    ):
        payload[field] = _money_str(Decimal(str(payload[field]))) if payload.get(field) is not None else None

    for item in payload.get("items", []):
        for field in (
            "quantity",
            "unit_price",
            "discount_amount",
            "tax_rate",
            "tax_amount",
            "line_total",
        ):
            if item.get(field) is not None:
                item[field] = _money_str(Decimal(str(item[field]))) if field != "quantity" else str(item[field])

    if payload.get("confidence") is not None:
        payload["confidence"] = float(payload["confidence"])

    return payload


router = APIRouter(
    prefix="/bills",
    tags=["Bills"],
)


class BillScanRequest(BaseModel):
    raw_text: str


def get_bill_extraction_service(
    db: AsyncSession = Depends(get_db),
) -> BillExtractionService:
    return BillExtractionService(db)


@router.post(
    "/scan-image",
    status_code=status.HTTP_200_OK,
)
async def scan_bill_image(
    file: UploadFile = File(...),
    organization_id: UUID = Depends(get_current_organization_id),
    service: BillExtractionService = Depends(get_bill_extraction_service),
) -> dict:
    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty image file provided.",
        )
    mime_type = file.content_type or "image/jpeg"
    extracted = await service.extract_from_image(contents, mime_type)
    normalized = extracted.model_dump(mode="json")
    return _normalize_extracted_payload(normalized)


@router.post(
    "/scan",
    status_code=status.HTTP_200_OK,
)
async def scan_bill(
    payload: BillScanRequest,
    organization_id: UUID = Depends(get_current_organization_id),
    service: BillExtractionService = Depends(get_bill_extraction_service),
) -> dict:
    if not payload.raw_text or not payload.raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bill text is required.",
        )

    extracted = await service.extract_from_text(payload.raw_text)

    normalized = extracted.model_dump(mode="json")
    return _normalize_extracted_payload(normalized)


@router.post(
    "/scan/confirm",
    status_code=status.HTTP_200_OK,
)
async def confirm_scan(
    payload: ExtractedBill,
    organization_id: UUID = Depends(get_current_organization_id),
    service: BillExtractionService = Depends(get_bill_extraction_service),
) -> dict:
    try:
        result = await service.confirm_extracted_bill(
            payload=payload,
            organization_id=organization_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    response = {
        "supplier_match": result["supplier_match"],
        "bill": BillResponse.model_validate(result["bill"]).model_dump(mode="json"),
    }
    return response
