from supabase import create_client
from app.core.config import SUPABASE_URL, SUPABASE_KEY
import logging
import json
from jose import jwt

logger = logging.getLogger(__name__)

# Use anon key for backend operations
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_authenticated_client(token: str):
    """Get a Supabase client with the user's JWT token."""
    try:
        logger.info("Creating authenticated Supabase client")
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Decode the token to get the refresh token
        try:
            # First try to decode without verification to get the refresh token
            unverified = jwt.get_unverified_claims(token)
            logger.debug(f"Unverified token payload: {unverified}")
            
            # Get the refresh token from the payload
            refresh_token = unverified.get("refresh_token", "")
            
            # Set the session with both tokens
            logger.debug("Setting session with tokens")
            client.auth.set_session(token, refresh_token)
            logger.info("Successfully created authenticated client")
            return client
        except Exception as e:
            logger.error(f"Error decoding token: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"Error creating authenticated client: {str(e)}", exc_info=True)
        raise
