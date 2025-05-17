from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from uuid import UUID

# Shared base model
class StoryBase(BaseModel):
    title: str
    content: str
    date: date

# Used when creating a story (from client input)
class StoryCreate(StoryBase):
    pass  # user_id and created_at are inferred

# Used when reading stories (returned from DB)
class Story(StoryBase):
    id: UUID
    created_at: datetime
    user_id: str
