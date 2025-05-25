from app.supabase.client import get_authenticated_client
from app.models.story import StoryCreate
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_all_stories(user_id: str, token: str):
    try:
        logger.info(f"Creating authenticated client for user {user_id}")
        client = get_authenticated_client(token)
        
        logger.info(f"Fetching stories for user {user_id}")
        result = client.table("stories").select("*").execute()
        
        if not result.data:
            logger.info(f"No stories found for user {user_id}")
            return []
            
        logger.info(f"Successfully fetched {len(result.data)} stories for user {user_id}")
        return result.data
    except Exception as e:
        logger.error(f"Error fetching stories for user {user_id}: {str(e)}", exc_info=True)
        raise

def get_story_by_id(story_id: int, token: str):
    try:
        logger.info(f"Creating authenticated client for story {story_id}")
        client = get_authenticated_client(token)
        
        logger.info(f"Fetching story {story_id}")
        result = client.table("stories").select("*").eq("id", story_id).single().execute()
        
        if not result.data:
            logger.info(f"Story {story_id} not found")
            return None
            
        logger.info(f"Successfully fetched story {story_id}")
        return result.data
    except Exception as e:
        logger.error(f"Error fetching story {story_id}: {str(e)}", exc_info=True)
        raise

def create_story(story: StoryCreate, user_id: str, token: str) -> Dict[str, Any]:
    try:
        # Prepare the story data
        data = story.dict()
        data["user_id"] = user_id
        
        # Convert date string to date object if present, then back to ISO string for Supabase
        if data.get("date"):
            date_obj = datetime.fromisoformat(data["date"].split("T")[0]).date()
            data["date"] = date_obj.isoformat()
        
        logger.info(f"Creating story for user {user_id}")
        logger.debug(f"Story data: {data}")
        
        # Insert the story with the user's context
        client = get_authenticated_client(token)
        result = client.table("stories").insert(data).execute()
        
        if not result.data:
            logger.error(f"No data returned after story creation for user {user_id}")
            raise Exception("Failed to create story: No data returned")
            
        logger.info(f"Successfully created story for user {user_id}")
        return result.data[0]  # Return the first (and only) created story
        
    except Exception as e:
        logger.error(f"Error creating story for user {user_id}: {str(e)}", exc_info=True)
        raise Exception(f"Failed to create story: {str(e)}")

def update_story(story_id: int, story: StoryCreate, user_id: str, token: str) -> Dict[str, Any]:
    try:
        logger.info(f"Creating authenticated client for story {story_id}")
        client = get_authenticated_client(token)
        
        data = story.dict()
        logger.info(f"Updating story {story_id} for user {user_id}")
        logger.debug(f"Update data: {data}")
        
        result = client.table("stories").update(data).eq("id", story_id).execute()
        
        if not result.data:
            logger.error(f"No data returned after updating story {story_id}")
            raise Exception("Failed to update story: No data returned")
            
        logger.info(f"Successfully updated story {story_id}")
        return result.data[0]
    except Exception as e:
        logger.error(f"Error updating story {story_id} for user {user_id}: {str(e)}", exc_info=True)
        raise

def delete_story(story_id: int, user_id: str, token: str):
    try:
        logger.info(f"Creating authenticated client for story {story_id}")
        client = get_authenticated_client(token)
        
        logger.info(f"Deleting story {story_id} for user {user_id}")
        result = client.table("stories").delete().eq("id", story_id).execute()
        
        if not result.data:
            logger.error(f"No data returned after deleting story {story_id}")
            raise Exception("Failed to delete story: No data returned")
            
        logger.info(f"Successfully deleted story {story_id}")
        return result.data
    except Exception as e:
        logger.error(f"Error deleting story {story_id} for user {user_id}: {str(e)}", exc_info=True)
        raise
