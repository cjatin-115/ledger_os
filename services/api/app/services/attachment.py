import asyncio
from pathlib import Path
from uuid import UUID, uuid4

try:
    import boto3
except ImportError:
    boto3 = None
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.attachment import Attachment, AttachmentEntityType
from app.schemas.attachment import AttachmentResponse


class AttachmentService:
    ALLOWED_FILE_TYPES = {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def upload(
        self,
        organization_id: UUID,
        uploaded_by: UUID,
        entity_type: AttachmentEntityType,
        entity_id: UUID,
        file: UploadFile,
    ) -> AttachmentResponse:
        if settings.ENVIRONMENT == "production" and settings.STORAGE_BACKEND != "s3":
            raise ValueError("Production attachments require S3 storage.")

        if file.content_type not in self.ALLOWED_FILE_TYPES:
            raise ValueError("Unsupported attachment file type.")

        file_name = Path(file.filename or "attachment").name
        if not file_name or len(file_name) > 255:
            raise ValueError("Attachment filename is invalid.")

        storage_key = f"{organization_id}/{entity_type.value}/{entity_id}/{uuid4()}"
        file_size = 0
        content = bytearray()
        try:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > settings.MAX_ATTACHMENT_SIZE_BYTES:
                    raise ValueError("Attachment exceeds the size limit.")
                content.extend(chunk)

            if settings.STORAGE_BACKEND == "s3":
                await asyncio.to_thread(
                    self._s3_client().put_object,
                    Bucket=settings.STORAGE_BUCKET,
                    Key=storage_key,
                    Body=bytes(content),
                    ContentType=file.content_type,
                )
            else:
                destination = Path(settings.STORAGE_ROOT) / storage_key
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)

            attachment = Attachment(
                organization_id=organization_id,
                entity_type=entity_type,
                entity_id=entity_id,
                file_name=file_name,
                file_type=file.content_type,
                storage_key=storage_key,
                file_size=file_size,
                uploaded_by=uploaded_by,
            )
            self.db.add(attachment)
            await self.db.commit()
            await self.db.refresh(attachment)
            return AttachmentResponse.model_validate(attachment)
        except Exception:
            if settings.STORAGE_BACKEND == "s3":
                await asyncio.to_thread(self._delete_s3_object, storage_key)
            else:
                destination = Path(settings.STORAGE_ROOT) / storage_key
                destination.unlink(missing_ok=True)
            await self.db.rollback()
            raise

    @staticmethod
    def _s3_client():
        if boto3 is None:
            raise RuntimeError("boto3 is required for S3 storage.")
        return boto3.client(
            "s3",
            endpoint_url=settings.STORAGE_ENDPOINT_URL,
            region_name=settings.STORAGE_REGION,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY_ID,
            aws_secret_access_key=settings.STORAGE_SECRET_ACCESS_KEY,
        )

    def _delete_s3_object(self, storage_key: str) -> None:
        self._s3_client().delete_object(
            Bucket=settings.STORAGE_BUCKET,
            Key=storage_key,
        )

    async def list(
        self,
        organization_id: UUID,
        entity_type: AttachmentEntityType,
        entity_id: UUID,
    ) -> list[AttachmentResponse]:
        result = await self.db.execute(
            select(Attachment)
            .where(
                Attachment.organization_id == organization_id,
                Attachment.entity_type == entity_type,
                Attachment.entity_id == entity_id,
            )
            .order_by(Attachment.created_at.desc())
        )
        return [AttachmentResponse.model_validate(attachment) for attachment in result.scalars().all()]
