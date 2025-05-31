from supabase import create_client, Client
from app.core.config import settings
import logging
import json
from jose import jwt

logger = logging.getLogger(__name__)

# Use anon key for backend operations
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_authenticated_client(token: str) -> Client:
    """
    Create an authenticated Supabase client with the provided token.
    """
    try:
        logger.info("Creating Supabase client...")
        logger.info(f"Supabase URL: {settings.SUPABASE_URL}")
        logger.info(f"Supabase Key: {settings.SUPABASE_KEY[:10]}...")
        logger.info(f"Token (first 20 chars): {token[:20]}...")
        
        # Create the client with the API key
        client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        
        # Verify the token
        user = client.auth.get_user(token)
        if not user:
            raise Exception("Invalid token")
            
        logger.info("Supabase client created successfully")
        return client
        
    except Exception as e:
        logger.error(f"Error creating Supabase client: {str(e)}", exc_info=True)
        raise
