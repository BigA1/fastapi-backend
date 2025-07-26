from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class InterviewSessionBase(BaseModel):
    user_id: str
    initial_context: Optional[str] = None
    status: str = "active"  # active, completed, abandoned

class InterviewSessionCreate(InterviewSessionBase):
    pass

class InterviewSession(InterviewSessionBase):
    id: int
    session_id: str
    conversation: List[Dict[str, str]] = []
    current_question: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    last_updated: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InterviewResponse(BaseModel):
    user_response: str

class InterviewStart(BaseModel):
    initial_context: Optional[str] = None

class InterviewContinue(BaseModel):
    session_id: str
    user_response: str

class InterviewEnd(BaseModel):
    session_id: str

class MemoryFromInterview(BaseModel):
    session_id: str
    title: str
    content: str
    date: Optional[str] = None  # Can be date string, year, or description
    date_type: Optional[str] = None  # 'exact', 'month', 'year', 'age', 'period'
    date_description: Optional[str] = None  # For age or period descriptions 