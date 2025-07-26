from fastapi import APIRouter, Depends, HTTPException, status
from app.models.interview import (
    InterviewStart, InterviewContinue, InterviewEnd, 
    InterviewSession, MemoryFromInterview
)
from app.services.ai_interviewer import AIInterviewerService
from app.core.auth import get_current_user
from app.services.memory_service import MemoryService
from app.services.interview_session_service import InterviewSessionService
from app.models.memory import MemoryCreate
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()
interviewer_service = AIInterviewerService()
memory_service = MemoryService()
session_service = InterviewSessionService()

@router.post("/start", response_model=Dict[str, Any])
async def start_interview(
    interview_start: InterviewStart,
    current_user: dict = Depends(get_current_user)
):
    """Start a new AI interview session."""
    try:
        logger.info(f"Starting interview for user {current_user['id']}")
        
        session_data = await interviewer_service.start_interview(
            user_id=current_user['id'],
            initial_context=interview_start.initial_context
        )
        
        # Store session in database
        session = await session_service.create_session(
            session_data=session_data,
            user_id=current_user['id'],
            token=current_user['token']
        )
        
        logger.info(f"Interview session started: {session.session_id}")
        return session.dict()
        
    except Exception as e:
        logger.error(f"Error starting interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start interview: {str(e)}"
        )

@router.post("/continue", response_model=Dict[str, Any])
async def continue_interview(
    interview_continue: InterviewContinue,
    current_user: dict = Depends(get_current_user)
):
    """Continue an active interview session with a user response."""
    try:
        session_id = interview_continue.session_id
        user_response = interview_continue.user_response
        
        logger.info(f"Continuing interview session {session_id}")
        
        # Get session from database
        session = await session_service.get_session(
            session_id=session_id,
            user_id=current_user['id'],
            token=current_user['token']
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        # Convert session to dict for AI service
        session_data = session.dict()
        
        # Continue interview
        updated_session_data = await interviewer_service.continue_interview(
            session_data, user_response
        )
        
        # Update session in database
        updated_session = await session_service.update_session(
            session_id=session_id,
            session_data=updated_session_data,
            user_id=current_user['id'],
            token=current_user['token']
        )
        
        logger.info(f"Interview continued for session {session_id}")
        return updated_session.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error continuing interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to continue interview: {str(e)}"
        )

@router.post("/end", response_model=Dict[str, Any])
async def end_interview(
    interview_end: InterviewEnd,
    current_user: dict = Depends(get_current_user)
):
    """End an interview session and generate a summary."""
    try:
        session_id = interview_end.session_id
        
        logger.info(f"Ending interview session {session_id}")
        
        # Get session from database
        session = await session_service.get_session(
            session_id=session_id,
            user_id=current_user['id'],
            token=current_user['token']
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        # Convert session to dict for AI service
        session_data = session.dict()
        
        # End interview and generate summary
        final_session_data = await interviewer_service.end_interview(session_data)
        
        # Update session in database
        final_session = await session_service.update_session(
            session_id=session_id,
            session_data=final_session_data,
            user_id=current_user['id'],
            token=current_user['token']
        )
        
        logger.info(f"Interview ended for session {session_id}")
        return final_session.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end interview: {str(e)}"
        )

@router.post("/create-memory", response_model=Dict[str, Any])
async def create_memory_from_interview(
    memory_data: MemoryFromInterview,
    current_user: dict = Depends(get_current_user)
):
    """Create a memory from an interview session."""
    try:
        session_id = memory_data.session_id
        
        logger.info(f"Creating memory from interview session {session_id}")
        
        # Get session from database
        session = await session_service.get_session(
            session_id=session_id,
            user_id=current_user['id'],
            token=current_user['token']
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        # Handle different date formats
        memory_date = None
        if memory_data.date:
            if memory_data.date_type == 'exact':
                try:
                    memory_date = datetime.fromisoformat(memory_data.date)
                except ValueError:
                    memory_date = datetime.now()
            elif memory_data.date_type == 'month':
                try:
                    # Add day 1 to month string
                    memory_date = datetime.fromisoformat(f"{memory_data.date}-01")
                except ValueError:
                    memory_date = datetime.now()
            elif memory_data.date_type == 'year':
                try:
                    # Add January 1st to year
                    memory_date = datetime.fromisoformat(f"{memory_data.date}-01-01")
                except ValueError:
                    memory_date = datetime.now()
            elif memory_data.date_type in ['age', 'period']:
                # For age and period, store the description in content or use current date
                memory_date = datetime.now()
                # Could also store the description in a separate field if needed
            else:
                memory_date = datetime.now()
        else:
            memory_date = datetime.now()
        
        # Create memory
        memory_create = MemoryCreate(
            title=memory_data.title,
            content=memory_data.content,
            date=memory_date
        )
        
        memory = await memory_service.create_memory(
            memory=memory_create,
            user_id=current_user['id'],
            token=current_user['token']
        )
        
        # Mark session as completed
        await session_service.update_session(
            session_id=session_id,
            session_data={'status': 'completed'},
            user_id=current_user['id'],
            token=current_user['token']
        )
        
        logger.info(f"Memory created from interview session {session_id}")
        return {
            "memory": memory,
            "session_id": session_id,
            "message": "Memory created successfully from interview"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating memory from interview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create memory: {str(e)}"
        )

@router.get("/sessions", response_model=List[Dict[str, Any]])
async def get_user_sessions(
    current_user: dict = Depends(get_current_user)
):
    """Get all active interview sessions for the current user."""
    try:
        sessions = await session_service.get_user_sessions(
            user_id=current_user['id'],
            token=current_user['token']
        )
        
        return [session.dict() for session in sessions]
        
    except Exception as e:
        logger.error(f"Error getting user sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )

@router.get("/suggest-title/{session_id}")
async def suggest_memory_title(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a suggested title for a memory based on the interview conversation."""
    try:
        session = await session_service.get_session(
            session_id=session_id,
            user_id=current_user['id'],
            token=current_user['token']
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interview session not found"
            )
        
        conversation = session.conversation
        suggested_title = await interviewer_service.suggest_memory_title(conversation)
        
        return {"suggested_title": suggested_title}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suggesting title: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to suggest title: {str(e)}"
        ) 