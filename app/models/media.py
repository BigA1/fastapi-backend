from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MediaBase(BaseModel):
    """Base model for media attachments."""
    media_type: str
    label: Optional[str] = None
    file_path: str

class MediaCreate(MediaBase):
    """Model for creating a new media attachment."""
    memory_id: int
    user_id: str

class Media(MediaBase):
    """Model for media attachment responses."""
    id: int
    memory_id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 