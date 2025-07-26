from app.supabase.client import get_authenticated_client
from app.models.interview import InterviewSession, InterviewSessionCreate
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class InterviewSessionService:
    def __init__(self):
        self.table = "interview_sessions"

    async def create_session(self, session_data: Dict[str, Any], user_id: str, token: str) -> InterviewSession:
        """Create a new interview session in the database."""
        try:
            logger.info(f"Creating interview session for user {user_id}")
            
            supabase = get_authenticated_client(token)
            
            # Create session using RPC function (bypasses RLS)
            response = supabase.rpc(
                'create_interview_session_for_user',
                {
                    'p_session_id': session_data['session_id'],
                    'p_user_id': user_id,
                    'p_initial_context': session_data.get('initial_context'),
                    'p_conversation': session_data.get('conversation', []),
                    'p_current_question': session_data.get('current_question'),
                    'p_status': session_data.get('status', 'active')
                }
            ).execute()
            
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create interview session")
            
            session_record = response.data
            return InterviewSession(**session_record)
            
        except Exception as e:
            logger.error(f"Error creating interview session: {str(e)}")
            raise

    async def get_session(self, session_id: str, user_id: str, token: str) -> Optional[InterviewSession]:
        """Get an interview session by session_id."""
        try:
            supabase = get_authenticated_client(token)
            
            response = supabase.rpc(
                'get_interview_session_for_user',
                {
                    'p_session_id': session_id,
                    'p_user_id': user_id
                }
            ).execute()
            
            if not response.data:
                return None
            
            session_record = response.data
            return InterviewSession(**session_record)
            
        except Exception as e:
            logger.error(f"Error getting interview session: {str(e)}")
            raise

    async def update_session(self, session_id: str, session_data: Dict[str, Any], user_id: str, token: str) -> InterviewSession:
        """Update an interview session."""
        try:
            supabase = get_authenticated_client(token)
            
            # Update session using RPC function (bypasses RLS)
            response = supabase.rpc(
                'update_interview_session_for_user',
                {
                    'p_session_id': session_id,
                    'p_user_id': user_id,
                    'p_conversation': session_data.get('conversation'),
                    'p_current_question': session_data.get('current_question'),
                    'p_summary': session_data.get('summary'),
                    'p_status': session_data.get('status'),
                    'p_ended_at': session_data.get('ended_at')
                }
            ).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Interview session not found")
            
            session_record = response.data
            return InterviewSession(**session_record)
            
        except Exception as e:
            logger.error(f"Error updating interview session: {str(e)}")
            raise

    async def get_user_sessions(self, user_id: str, token: str) -> List[InterviewSession]:
        """Get all interview sessions for a user."""
        try:
            supabase = get_authenticated_client(token)
            
            response = supabase.rpc(
                'get_interview_sessions_for_user',
                {'user_uuid': user_id}
            ).execute()
            
            sessions = []
            for session_record in response.data:
                sessions.append(InterviewSession(**session_record))
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {str(e)}")
            raise

    async def delete_session(self, session_id: str, user_id: str, token: str) -> bool:
        """Delete an interview session."""
        try:
            supabase = get_authenticated_client(token)
            
            response = supabase.table(self.table).delete().eq('session_id', session_id).eq('user_id', user_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting interview session: {str(e)}")
            raise 