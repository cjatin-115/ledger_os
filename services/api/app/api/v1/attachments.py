from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_organization_id,
    get_current_user_id,
    require_permission,
)
from app.db.models.attachment import AttachmentEntityType
from app.db.session import get_db
from app.schemas.attachment import AttachmentResponse
from app.services.attachment import AttachmentService

router = APIRouter(prefix="/attachments", tags=["Attachments"])


@router.post(
    "/{entity_type}/{entity_id}",
    response_model=AttachmentResponse,
    status_code=201,
)
async def upload_attachment(
    entity_type: AttachmentEntityType,
    entity_id: UUID,
    file: UploadFile = File(...),
    organization_id: UUID = Depends(get_current_organization_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("attachments.write")),
) -> AttachmentResponse:
    return await AttachmentService(db).upload(
        organization_id=organization_id,
        uploaded_by=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        file=file,
    )


@router.get(
    "/{entity_type}/{entity_id}",
    response_model=list[AttachmentResponse],
)
async def list_attachments(
    entity_type: AttachmentEntityType,
    entity_id: UUID,
    organization_id: UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(require_permission("attachments.read")),
) -> list[AttachmentResponse]:
    return await AttachmentService(db).list(
        organization_id=organization_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )