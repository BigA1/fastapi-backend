from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

# Media attachment model
class MediaAttachmentBase(BaseModel):
    media_type: str
    label: Optional[str] = None

# Used when creating a media attachment
class MediaAttachmentCreate(MediaAttachmentBase):
    memory_id: int
    file_path: str
    user_id: str

class MediaAttachment(MediaAttachmentBase):
    id: int
    memory_id: int
    file_path: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Shared base model
class MemoryBase(BaseModel):
    title: str
    content: str
    date: Optional[datetime] = None

# Used when creating a memory (from client input)
class MemoryCreate(MemoryBase):
    pass  # user_id and created_at are inferred

# Used when reading memories (returned from DB)
class Memory(MemoryBase):
    id: int
    created_at: datetime
    user_id: str
    updated_at: datetime
    media_attachments: List[MediaAttachment] = []

    class Config:
        from_attributes = True

# Used when updating a memory
class MemoryUpdate(MemoryBase):
    title: Optional[str] = None
    content: Optional[str] = None
    date: Optional[str] = None
