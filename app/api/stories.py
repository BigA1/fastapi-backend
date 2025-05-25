from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.story import StoryCreate, StoryUpdate
from app.services.story_service import get_all_stories, get_story_by_id, create_story, update_story, delete_story
from app.core.auth import get_current_user
from typing import List, Dict, Any, Optional
import logging
from app.supabase.client import get_authenticated_client

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/search")
async def search_stories(
    query: Optional[str] = Query(None, description="Search query for story title and content"),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user)
):
    """Search stories by text and date range."""
    try:
        logger.info(f"Search parameters - query: {query}, start_date: {start_date}, end_date: {end_date}")
        
        # Get authenticated Supabase client
        supabase = get_authenticated_client(current_user["token"])
        
        # Add text search if query provided
        if query:
            # Convert query to tsquery format
            formatted_query = query.replace(' ', ' & ')  # Convert spaces to & for AND operation
            logger.info(f"Formatted search query: {formatted_query}")
            
            # Use RPC for full-text search
            response = supabase.rpc(
                'search_stories',
                {
                    'search_query': formatted_query,
                    'user_id': current_user["id"]
                }
            ).execute()
            
            # Add date range filtering if needed
            if start_date or end_date:
                stories = response.data
                if start_date:
                    stories = [s for s in stories if s['date'] >= start_date]
                if end_date:
                    stories = [s for s in stories if s['date'] <= end_date]
                response.data = stories
                
        else:
            # If no search query, use regular query with date filters
            search_query = supabase.table("stories") \
                .select("*, media_attachments(*)") \
                .eq("user_id", current_user["id"])
            
            if start_date:
                search_query = search_query.gte("date", start_date)
            if end_date:
                search_query = search_query.lte("date", end_date)
                
            response = search_query.execute()
        
        logger.info(f"Search response: {response}")
        
        # Filter media attachments in Python if needed
        if query and response.data:
            for story in response.data:
                if story.get('media_attachments'):
                    story['media_attachments'] = [
                        media for media in story['media_attachments']
                        if media.get('label') and query.lower() in media['label'].lower()
                    ]
        
        return response.data
        
    except Exception as e:
        logger.error(f"Error searching stories: {str(e)}", exc_info=True)
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching stories: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
async def list_stories(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        logger.info(f"Fetching stories for user {current_user.get('id')}")
        logger.debug(f"User data: {current_user}")
        
        if not current_user.get("token"):
            logger.error("No token found in current_user")
            raise HTTPException(status_code=401, detail="No authentication token found")
            
        stories = get_all_stories(current_user["id"], current_user["token"])
        logger.info(f"Successfully fetched {len(stories)} stories")
        return stories
    except Exception as e:
        logger.error(f"Error in list_stories: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{story_id}", response_model=Dict[str, Any])
async def get_story(story_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        logger.info(f"Fetching story {story_id} for user {current_user.get('id')}")
        story = get_story_by_id(story_id, current_user["token"])
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        return story
    except Exception as e:
        logger.error(f"Error in get_story: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Dict[str, Any])
async def create_new_story(story: StoryCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        logger.info(f"Creating story for user {current_user.get('id')}")
        return create_story(story, current_user["id"], current_user["token"])
    except Exception as e:
        logger.error(f"Error in create_new_story: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{story_id}", response_model=Dict[str, Any])
async def update_existing_story(story_id: int, story: StoryCreate, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        logger.info(f"Updating story {story_id} for user {current_user.get('id')}")
        return update_story(story_id, story, current_user["id"], current_user["token"])
    except Exception as e:
        logger.error(f"Error in update_existing_story: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{story_id}")
async def delete_existing_story(story_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        logger.info(f"Deleting story {story_id} for user {current_user.get('id')}")
        return delete_story(story_id, current_user["id"], current_user["token"])
    except Exception as e:
        logger.error(f"Error in delete_existing_story: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{story_id}/media")
async def get_story_media(
    story_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get media for a specific story."""
    try:
        logger.info(f"Fetching media for story {story_id}")
        
        # Get authenticated Supabase client
        supabase = get_authenticated_client(current_user["token"])
        
        # Query the media_attachments table for this story
        response = supabase.table("media_attachments") \
            .select("*") \
            .eq("story_id", story_id) \
            .execute()
            
        logger.info(f"Media response data: {response.data}")
        return response.data
        
    except Exception as e:
        logger.error(f"Error in get_story_media: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching media: {str(e)}"
        )
