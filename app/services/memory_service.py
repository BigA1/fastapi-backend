from app.supabase.client import get_authenticated_client
from app.models.memory import MemoryCreate, Memory
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self):
        self.table = "memories"

    async def create_memory(self, memory: MemoryCreate, user_id: str, token: str) -> Memory:
        try:
            logger.info(f"Creating memory for user {user_id}")
            logger.info(f"Token (first 20 chars): {token[:20]}...")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            # Create memory using RPC
            response = supabase.rpc(
                'create_memory_for_user',
                {
                    'title': memory.title,
                    'content': memory.content,
                    'date': memory.date.isoformat(),
                    'user_id': user_id
                }
            ).execute()
            
            logger.info(f"Memory creation response: {response.data}")
            
            if not response.data:
                logger.error("No data returned from insert operation")
                raise HTTPException(status_code=500, detail="Failed to create memory")
            
            # Ensure all required fields are present
            memory_data = response.data
            if isinstance(memory_data, dict):
                # Add updated_at if not present
                if 'updated_at' not in memory_data:
                    memory_data['updated_at'] = memory_data.get('created_at')
                
                # Convert to Memory model to validate
                try:
                    return Memory(**memory_data)
                except Exception as e:
                    logger.error(f"Error validating memory data: {str(e)}")
                    logger.error(f"Memory data: {memory_data}")
                    raise HTTPException(status_code=500, detail="Invalid memory data returned")
            else:
                raise HTTPException(status_code=500, detail="Invalid response format")
            
        except Exception as e:
            logger.error(f"Error creating memory: {str(e)}", exc_info=True)
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No details available'}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_memory(self, memory_id: int, user_id: str, token: str) -> Memory:
        try:
            logger.info(f"Fetching memory {memory_id} for user {user_id}")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            # Get memory using RPC
            response = supabase.rpc(
                'get_memory_for_user',
                {
                    'memory_id': memory_id,
                    'user_id': user_id
                }
            ).execute()
                
            logger.info(f"Memory fetch response: {response.data}")
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Memory not found")
            
            # Ensure all required fields are present
            memory_data = response.data[0]
            if isinstance(memory_data, dict):
                # Add updated_at if not present
                if 'updated_at' not in memory_data:
                    memory_data['updated_at'] = memory_data.get('created_at')
                
                # Convert to Memory model to validate
                try:
                    return Memory(**memory_data)
                except Exception as e:
                    logger.error(f"Error validating memory data: {str(e)}")
                    logger.error(f"Memory data: {memory_data}")
                    raise HTTPException(status_code=500, detail="Invalid memory data returned")
            else:
                raise HTTPException(status_code=500, detail="Invalid response format")
            
        except Exception as e:
            logger.error(f"Error fetching memory: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def get_memories(self, user_id: str, token: str) -> List[Memory]:
        """Get all memories for a user."""
        try:
            logger.info(f"MemoryService.get_memories called for user_id: {user_id}")
            logger.info(f"Token (first 20 chars): {token[:20]}...")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            logger.info("Created authenticated Supabase client in service")
            
            # Query memories
            query = supabase.table(self.table) \
                .select("id, title, content, date, user_id, created_at, media_attachments(*)") \
                .eq("user_id", user_id) \
                .order("date", desc=True)
                
            logger.info("Executing Supabase query...")
            response = query.execute()
            logger.info(f"Query response: {response}")
            
            if not response.data:
                logger.info("No memories found in response data")
                return []
            
            logger.info(f"Found {len(response.data)} memories")
            
            # Convert to Memory objects
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
            return memories
            
        except Exception as e:
            logger.error(f"Error in get_memories: {str(e)}", exc_info=True)
            raise

    async def update_memory(self, memory_id: int, memory: MemoryCreate, user_id: str, token: str) -> Memory:
        try:
            logger.info(f"Updating memory {memory_id} for user {user_id}")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            # Update memory using RPC
            response = supabase.rpc(
                'update_memory_for_user',
                {
                    'memory_id': memory_id,
                    'title': memory.title,
                    'content': memory.content,
                    'date': memory.date.isoformat(),
                    'user_id': user_id
                }
            ).execute()
                
            logger.info(f"Memory update response: {response.data}")
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Memory not found or access denied")
            
            # Ensure all required fields are present
            memory_data = response.data
            if isinstance(memory_data, dict):
                # Add updated_at if not present
                if 'updated_at' not in memory_data:
                    memory_data['updated_at'] = memory_data.get('created_at')
                
                # Convert to Memory model to validate
                try:
                    return Memory(**memory_data)
                except Exception as e:
                    logger.error(f"Error validating memory data: {str(e)}")
                    logger.error(f"Memory data: {memory_data}")
                    raise HTTPException(status_code=500, detail="Invalid memory data returned")
            else:
                raise HTTPException(status_code=500, detail="Invalid response format")
            
        except Exception as e:
            logger.error(f"Error updating memory: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_memory(self, memory_id: int, user_id: str, token: str):
        try:
            logger.info(f"Deleting memory {memory_id} for user {user_id}")
            
            # Get authenticated Supabase client
            supabase = get_authenticated_client(token)
            
            # Delete memory using RPC
            response = supabase.rpc(
                'delete_memory_for_user',
                {
                    'memory_id': memory_id,
                    'user_id': user_id
                }
            ).execute()
                
            logger.info(f"Memory deletion response: {response.data}")
            
            if not response.data:
                raise HTTPException(status_code=404, detail="Memory not found or access denied")
            
            # Ensure all required fields are present
            memory_data = response.data
            if isinstance(memory_data, dict):
                # Add updated_at if not present
                if 'updated_at' not in memory_data:
                    memory_data['updated_at'] = memory_data.get('created_at')
                
                # Convert to Memory model to validate
                try:
                    return Memory(**memory_data)
                except Exception as e:
                    logger.error(f"Error validating memory data: {str(e)}")
                    logger.error(f"Memory data: {memory_data}")
                    raise HTTPException(status_code=500, detail="Invalid memory data returned")
            else:
                raise HTTPException(status_code=500, detail="Invalid response format")
            
        except Exception as e:
            logger.error(f"Error deleting memory: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
