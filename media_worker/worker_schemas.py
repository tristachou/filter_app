from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class MediaItemBase(BaseModel):
    owner_id: UUID
    original_filename: str
    storage_path: str
    media_type: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)

class MediaItemInDB(MediaItemBase):
    id: UUID = Field(default_factory=uuid4)
    is_processed: bool = False # Add this field for processed items
    original_media_id: Optional[UUID] = None # Link back to original
