from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.memory import MemoryCreate, MemoryUpdate, Memory
from app.services.memory_service import MemoryService
from app.core.auth import get_current_user
from typing import List, Dict, Any, Optional
import logging
from app.supabase.client import get_authenticated_client

logger = logging.getLogger(__name__)

router = APIRouter()
memory_service = MemoryService()

@router.get("/search")
async def search_memories(
    query: Optional[str] = Query(None, description="Search query for memory title and content"),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user)
):
    """Search memories by text and date range."""
    try:
        logger.info(f"Search parameters - query: {query}, start_date: {start_date}, end_date: {end_date}")
        
        # Get authenticated Supabase client
        supabase = get_authenticated_client(current_user["token"])
        
        # Get all memories for the user
        response = supabase.rpc(
            'get_memories_for_user',
            {'user_id': current_user["id"]}
        ).execute()
        
        memories = response.data
        
        # Filter by search query if provided
        if query:
            query = query.lower()
            memories = [
                memory for memory in memories
                if (memory.get('title', '').lower().find(query) != -1 or
                    memory.get('content', '').lower().find(query) != -1)
            ]
        
        # Filter by date range if provided
        if start_date:
            memories = [m for m in memories if m['date'] >= start_date]
        if end_date:
            memories = [m for m in memories if m['date'] <= end_date]
        
        logger.info(f"Found {len(memories)} matching memories")
        return memories
        
    except Exception as e:
        logger.error(f"Error searching memories: {str(e)}", exc_info=True)
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching memories: {str(e)}"
        )

@router.get("/", response_model=List[Memory])
async def get_memories(
    current_user: dict = Depends(get_current_user)
):
    try:
        logger.info("="*50)
        logger.info("GET /memories/ endpoint called")
        logger.info(f"Current user: {current_user}")
        logger.info(f"User ID: {current_user.get('id')}")
        logger.info(f"Token: {current_user.get('token')[:20]}...")
        
        # Get authenticated Supabase client
        supabase = get_authenticated_client(current_user["token"])
        logger.info("Created authenticated Supabase client")
        
        # Query memories using RPC
        logger.info("-"*50)
        logger.info("Querying memories...")
        
        response = supabase.rpc(
            'get_memories_for_user',
            {'user_id': current_user["id"]}
        ).execute()
            
        logger.info(f"Raw Supabase response: {response}")
        logger.info(f"Number of memories found: {len(response.data)}")
        
        # Convert to Memory objects
        logger.info("-"*50)
        logger.info("Converting memories to objects...")
        memories = []
        for memory_data in response.data:
            try:
                # Use created_at as updated_at since we don't have an updated_at column
                memory_data['updated_at'] = memory_data.get('created_at')
                memory = Memory(**memory_data)
                memories.append(memory)
                logger.info(f"Successfully converted memory {memory.id}")
            except Exception as e:
                logger.error(f"Error converting memory data: {str(e)}", exc_info=True)
                logger.error(f"Memory data: {memory_data}")
        
        logger.info(f"Returning {len(memories)} memories")
        logger.info("="*50)
        return memories
        
    except Exception as e:
        logger.error(f"Error in get_memories endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{memory_id}", response_model=Memory)
async def get_memory(
    memory_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        return await memory_service.get_memory(memory_id, current_user["id"], current_user["token"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Memory)
async def create_memory(
    memory: MemoryCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        return await memory_service.create_memory(memory, current_user["id"], current_user["token"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{memory_id}", response_model=Memory)
async def update_memory(
    memory_id: int,
    memory: MemoryCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        return await memory_service.update_memory(memory_id, memory, current_user["id"], current_user["token"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        return await memory_service.delete_memory(memory_id, current_user["id"], current_user["token"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{memory_id}/media")
async def get_memory_media(
    memory_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get media for a specific memory."""
    try:
        logger.info(f"Fetching media for memory {memory_id}")
        
        # Get authenticated Supabase client
        supabase = get_authenticated_client(current_user["token"])
        
        # Query media using RPC
        response = supabase.rpc(
            'get_memory_media_for_user',
            {
                'memory_id': memory_id,
                'user_id': current_user["id"]
            }
        ).execute()
            
        logger.info(f"Media response data: {response.data}")
        return response.data
        
    except Exception as e:
        logger.error(f"Error in get_memory_media: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching media: {str(e)}"
        )
