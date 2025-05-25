from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

# Shared base model
class StoryBase(BaseModel):
    title: str
    content: str
    date: Optional[str] = None  # Accept date as string in ISO format

# Used when creating a story (from client input)
class StoryCreate(StoryBase):
    pass  # user_id and created_at are inferred

# Used when reading stories (returned from DB)
class Story(StoryBase):
    id: int
    created_at: datetime
    user_id: str

# Media attachment model
class MediaAttachment(BaseModel):
    id: int
    story_id: int
    file_path: str
    media_type: str  # 'image' or 'audio'
    created_at: datetime
    user_id: str

# Used when creating a media attachment
class MediaAttachmentCreate(BaseModel):
    story_id: int
    file_path: str
    media_type: str
    user_id: str
