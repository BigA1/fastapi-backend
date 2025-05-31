from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, status, Form
from app.models.memory import MediaAttachmentCreate
from app.services.media_service import MediaService
from app.core.auth import get_current_user
import logging
from app.supabase.client import get_authenticated_client
import uuid
import os
from fastapi.responses import FileResponse
import tempfile
from pydantic import BaseModel
from typing import Optional
from app.models.media import MediaCreate, Media

logger = logging.getLogger(__name__)
router = APIRouter(tags=["media"])
media_service = MediaService()

class MediaUpdate(BaseModel):
    label: str | None = None

@router.get("/story/{story_id}")
async def get_story_media(
    story_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        logger.info(f"Fetching media for story {story_id}")
        
        # Get authenticated Supabase client
        supabase = get_authenticated_client(current_user["token"])
        
        # Query the media_attachments table for this story
        response = supabase.table("media_attachments") \
            .select("*") \
            .eq("story_id", story_id) \
            .execute()
            
        logger.info(f"Story media response: {response.data}")
        return response.data
        
    except Exception as e:
        logger.error(f"Error getting story media: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    memory_id: int = Form(...),
    media_type: str = Form(...),
    label: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Upload a media file for a memory."""
    try:
        media_data = MediaCreate(
            memory_id=memory_id,
            media_type=media_type,
            label=label,
            file_path="",  # Will be set by the service
            user_id=current_user["id"]
        )
        
        return await media_service.upload_media(
            file=file,
            media_data=media_data,
            user_id=current_user["id"],
            token=current_user["token"]
        )
        
    except Exception as e:
        logger.error(f"Error in upload_media: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        logger.info(f"Deleting media {media_id}")
        
        # Get authenticated Supabase client
        supabase = get_authenticated_client(current_user["token"])
        
        # Get media record first to get the file path
        response = supabase.table("media_attachments") \
            .select("*") \
            .eq("id", media_id) \
            .single() \
            .execute()
            
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found"
            )
            
        media = response.data
        
        # Delete from storage
        bucket = "media"
        file_path = media["file_path"]
        supabase.storage.from_(bucket).remove([file_path])
        
        # Delete from database
        response = supabase.table("media_attachments") \
            .delete() \
            .eq("id", media_id) \
            .execute()
            
        logger.info(f"Media deletion response: {response.data}")
        return response.data[0] if response.data else None
        
    except Exception as e:
        logger.error(f"Error deleting media: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{media_id}/url")
async def get_media_url(
    media_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a signed URL for a media file."""
    try:
        return await media_service.get_media_url(
            media_id=media_id,
            user_id=current_user["id"],
            token=current_user["token"]
        )
        
    except Exception as e:
        logger.error(f"Error in get_media_url: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{media_id}/label")
async def update_media_label(
    media_id: int,
    label: str,
    current_user: dict = Depends(get_current_user)
):
    """Update the label of a media file."""
    try:
        return await media_service.update_media_label(
            media_id=media_id,
            label=label,
            user_id=current_user["id"],
            token=current_user["token"]
        )
        
    except Exception as e:
        logger.error(f"Error in update_media_label: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 