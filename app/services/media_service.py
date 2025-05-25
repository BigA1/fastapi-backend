from app.supabase.client import supabase
from app.models.story import MediaAttachmentCreate
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def get_story_media(story_id: int, token: str) -> List[Dict[str, Any]]:
    """Get all media attachments for a story"""
    try:
        # Set the auth token in the client's headers
        supabase.options.headers["Authorization"] = f"Bearer {token}"
        return supabase.table("media_attachments").select("*").eq("story_id", story_id).execute().data
    except Exception as e:
        logger.error(f"Error fetching media for story {story_id}: {str(e)}")
        raise

def create_media_attachment(media: MediaAttachmentCreate, user_id: str, token: str) -> Dict[str, Any]:
    """Create a new media attachment record"""
    try:
        # Set the auth token in the client's headers
        supabase.options.headers["Authorization"] = f"Bearer {token}"
        
        # Prepare the media data
        data = media.dict()
        data["user_id"] = user_id
        
        # Insert the media attachment
        result = supabase.table("media_attachments").insert(data).execute()
        
        if not result.data:
            raise Exception("Failed to create media attachment: No data returned")
            
        return result.data[0]
    except Exception as e:
        logger.error(f"Error creating media attachment for user {user_id}: {str(e)}")
        raise

def delete_media_attachment(media_id: int, user_id: str, token: str):
    """Delete a media attachment"""
    try:
        # Set the auth token in the client's headers
        supabase.options.headers["Authorization"] = f"Bearer {token}"
        
        # Get the media attachment to verify ownership and get file path
        media = supabase.table("media_attachments").select("*").eq("id", media_id).single().execute()
        
        if not media.data or media.data["user_id"] != user_id:
            raise Exception("Media attachment not found or unauthorized")
            
        # Delete the file from storage
        bucket = "media"  # Your Supabase storage bucket name
        file_path = media.data["file_path"]
        supabase.storage.from_(bucket).remove([file_path])
        
        # Delete the database record
        return supabase.table("media_attachments").delete().eq("id", media_id).execute().data
    except Exception as e:
        logger.error(f"Error deleting media attachment {media_id} for user {user_id}: {str(e)}")
        raise 