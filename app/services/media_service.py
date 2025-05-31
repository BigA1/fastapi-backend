from app.supabase.client import get_authenticated_client
from app.models.media import MediaCreate, Media
from typing import List, Optional
import logging
import os
import uuid
from fastapi import HTTPException
from datetime import datetime

logger = logging.getLogger(__name__)

class MediaService:
    def __init__(self):
        self.table = "media_attachments"
        self.bucket = "media"

    async def create_media(self, media: MediaCreate, memory_id: int, user_id: str, token: str) -> Media:
        try:
            logger.info(f"Creating media for memory {memory_id}")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            # Create media record
            media_data = media.dict()
            media_data["memory_id"] = memory_id
            media_data["user_id"] = user_id
            
            response = supabase.table(self.table) \
                .insert(media_data) \
                .execute()
                
            logger.info(f"Media creation response: {response.data}")
            
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to create media")
                
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error creating media: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def get_media(self, media_id: int, user_id: str, token: str) -> Media:
        try:
            logger.info(f"Fetching media {media_id}")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            response = supabase.table(self.table) \
                .select("*") \
                .eq("id", media_id) \
                .eq("user_id", user_id) \
                .single() \
                .execute()
                
            logger.info(f"Media fetch response: {response.data}")
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Media not found")
                
            return response.data
            
        except Exception as e:
            logger.error(f"Error fetching media: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def get_memory_media(self, memory_id: int, user_id: str, token: str) -> List[Media]:
        try:
            logger.info(f"Fetching media for memory {memory_id}")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            response = supabase.table(self.table) \
                .select("*") \
                .eq("memory_id", memory_id) \
                .eq("user_id", user_id) \
                .execute()
                
            logger.info(f"Memory media fetch response: {response.data}")
            
            if not response.data:
                return []
                
            return response.data
            
        except Exception as e:
            logger.error(f"Error fetching memory media: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def update_media(self, media_id: int, media: MediaCreate, user_id: str, token: str) -> Media:
        try:
            logger.info(f"Updating media {media_id}")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            # First check if the media exists and belongs to the user
            check_response = supabase.table(self.table) \
                .select("id") \
                .eq("id", media_id) \
                .eq("user_id", user_id) \
                .single() \
                .execute()
                
            if not check_response.data:
                raise HTTPException(status_code=404, detail="Media not found or access denied")
            
            # Update the media
            response = supabase.table(self.table) \
                .update(media.dict()) \
                .eq("id", media_id) \
                .eq("user_id", user_id) \
                .execute()
                
            logger.info(f"Media update response: {response.data}")
            
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to update media")
                
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error updating media: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_media(self, media_id: int, user_id: str, token: str):
        try:
            logger.info(f"Deleting media {media_id}")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            # First check if the media exists and belongs to the user
            check_response = supabase.table(self.table) \
                .select("id") \
                .eq("id", media_id) \
                .eq("user_id", user_id) \
                .single() \
                .execute()
                
            if not check_response.data:
                raise HTTPException(status_code=404, detail="Media not found or access denied")
            
            # Delete the media
            response = supabase.table(self.table) \
                .delete() \
                .eq("id", media_id) \
                .eq("user_id", user_id) \
                .execute()
                
            logger.info(f"Media deletion response: {response.data}")
            
            if not response.data:
                raise HTTPException(status_code=500, detail="Failed to delete media")
                
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error deleting media: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def upload_media(self, file, media_data: MediaCreate, user_id: str, token: str):
        try:
            logger.info(f"Uploading media for memory {media_data.memory_id} with type {media_data.media_type}")
            
            # Validate media type
            if media_data.media_type not in ["image", "audio"]:
                raise HTTPException(status_code=400, detail="Invalid media type")
                
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Upload to Supabase Storage
            file_path = f"{user_id}/{unique_filename}"
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            # Read file content
            content = await file.read()
            
            # Upload to storage
            result = supabase.storage.from_(self.bucket).upload(file_path, content)
            
            if not result:
                raise HTTPException(status_code=500, detail="Failed to upload file")
                
            # Create media attachment record
            media = MediaCreate(
                memory_id=media_data.memory_id,
                file_path=file_path,
                media_type=media_data.media_type,
                user_id=user_id,
                label=media_data.label
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

    async def get_media_url(self, media_id: int, user_id: str, token: str):
        try:
            logger.info(f"Fetching media {media_id} for user {user_id}")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            # Get media record
            response = supabase.table("media_attachments") \
                .select("*") \
                .eq("id", media_id) \
                .single() \
                .execute()
                
            logger.info(f"Media record response: {response.data}")
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Media not found")
                
            media = response.data
            
            # Get the file from Supabase Storage
            file_path = media["file_path"]
            
            # Create a signed URL that expires in 1 hour
            signed_url_response = supabase.storage.from_(self.bucket).create_signed_url(
                file_path,
                expires_in=3600  # 1 hour in seconds
            )
            
            logger.info(f"Generated signed URL response: {signed_url_response}")
            
            if not signed_url_response or "signedURL" not in signed_url_response:
                raise HTTPException(status_code=500, detail="Error generating signed URL")
                
            # Return the signed URL
            return signed_url_response["signedURL"]
                    
        except Exception as e:
            logger.error(f"Error serving media: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def update_media_label(self, media_id: int, label: str, user_id: str, token: str):
        try:
            logger.info(f"Updating media {media_id} with label: {label}")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            # First check if the media exists and belongs to the user
            check_response = supabase.table("media_attachments") \
                .select("id") \
                .eq("id", media_id) \
                .eq("user_id", user_id) \
                .single() \
                .execute()
                
            if not check_response.data:
                raise HTTPException(status_code=404, detail="Media not found or access denied")
            
            # Update the media record
            response = supabase.table("media_attachments") \
                .update({"label": label}) \
                .eq("id", media_id) \
                .eq("user_id", user_id) \
                .execute()
                
            logger.info(f"Media update response: {response.data}")
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"Error updating media: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e)) 