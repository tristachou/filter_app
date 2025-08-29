
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str
    hashed_password: str
    role: str = "user"
    filter_usage: Optional[Dict[str, int]] = Field(default_factory=dict)

class Token(BaseModel):
    access_token: str
    token_type: str

class MediaItemBase(BaseModel):
    owner_id: UUID
    original_filename: str
    storage_path: str
    media_type: str
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)

class MediaItemInDB(MediaItemBase):
    id: UUID = Field(default_factory=uuid4)

from typing import Optional, Dict

class FilterItemBase(BaseModel):
    name: str = Field(..., serialization_alias='filter_name')
    storage_path: str
    filter_type: str = "default"
    owner_id: Optional[UUID] = None

class FilterItemInDB(FilterItemBase):
    id: UUID = Field(default_factory=uuid4)

class ProcessRequest(BaseModel):
    media_id: UUID
    filter_id: UUID

class ProcessResponse(BaseModel):
    message: str
    processed_media_id: UUID
    processed_filename: str
