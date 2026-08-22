from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    entity_type: str
    entity_id: UUID
    file_name: str
    file_type: str
    file_size: int
    uploaded_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}