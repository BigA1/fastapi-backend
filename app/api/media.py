from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, status, Form
from app.models.story import MediaAttachmentCreate
from app.services import media_service
from app.core.auth import get_current_user
import logging
from app.supabase.client import get_authenticated_client
import uuid
import os
from fastapi.responses import FileResponse
import tempfile
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["media"])

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
    story_id: int = Form(None),
    media_type: str = Form(...),
    label: str | None = Form(None),
    current_user: dict = Depends(get_current_user)
):
    try:
        logger.info(f"Uploading media for story {story_id} with type {media_type}")
        
        # Validate media type
        if media_type not in ["image", "audio"]:
            raise HTTPException(status_code=400, detail="Invalid media type")
            
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Upload to Supabase Storage
        bucket = "media"
        file_path = f"{current_user['id']}/{unique_filename}"
        
        # Get authenticated Supabase client
        supabase = get_authenticated_client(current_user["token"])
        
        # Read file content
        content = await file.read()
        
        # Upload to storage
        result = supabase.storage.from_(bucket).upload(file_path, content)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to upload file")
            
        # Create media attachment record
        media = MediaAttachmentCreate(
            story_id=story_id,
            file_path=file_path,
            media_type=media_type,
            user_id=current_user["id"],  # Add user_id to satisfy RLS policy
            label=label
        )
        
        # Insert into media_attachments table
        response = supabase.table("media_attachments") \
            .insert(media.dict()) \
            .execute()
            
        logger.info(f"Media upload response: {response.data}")
        return response.data[0] if response.data else None
        
    except Exception as e:
        logger.error(f"Error uploading media: {str(e)}", exc_info=True)
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

@router.get("/{media_id}")
async def get_media(
    media_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a media file by ID."""
    try:
        logger.info(f"Fetching media {media_id} for user {current_user['id']}")
        
        # Get authenticated Supabase client
        supabase = get_authenticated_client(current_user["token"])
        
        # Get media record
        response = supabase.table("media_attachments") \
            .select("*") \
            .eq("id", media_id) \
            .single() \
            .execute()
            
        logger.info(f"Media record response: {response.data}")
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found"
            )
            
        media = response.data
        
        # Get the file from Supabase Storage
        file_path = media["file_path"]
        bucket = "media"
        
        # Create a signed URL that expires in 1 hour
        signed_url_response = supabase.storage.from_(bucket).create_signed_url(
            file_path,
            expires_in=3600  # 1 hour in seconds
        )
        
        logger.info(f"Generated signed URL response: {signed_url_response}")
        
        if not signed_url_response or "signedURL" not in signed_url_response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating signed URL"
            )
            
        # Return the signed URL
        return {"url": signed_url_response["signedURL"]}
                
    except Exception as e:
        logger.error(f"Error serving media: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error serving media: {str(e)}"
        )

@router.patch("/{media_id}")
async def update_media(
    media_id: int,
    update: MediaUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a media item's label."""
    try:
        logger.info(f"Updating media {media_id} with label: {update.label}")
        
        # Get authenticated Supabase client
        supabase = get_authenticated_client(current_user["token"])
        
        # First check if the media exists and belongs to the user
        check_response = supabase.table("media_attachments") \
            .select("id") \
            .eq("id", media_id) \
            .eq("user_id", current_user["id"]) \
            .single() \
            .execute()
            
        if not check_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found or access denied"
            )
        
        # Update the media record
        response = supabase.table("media_attachments") \
            .update({"label": update.label}) \
            .eq("id", media_id) \
            .eq("user_id", current_user["id"]) \
            .execute()
            
        logger.info(f"Media update response: {response.data}")
        return response.data[0] if response.data else None
        
    except Exception as e:
        logger.error(f"Error updating media: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 