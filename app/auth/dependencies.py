from fastapi import Request, HTTPException
import logging
from app.supabase.client import supabase

logger = logging.getLogger(__name__)

def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid auth token")

    token = auth_header.split(" ")[1]

    try:
        # Use Supabase client to verify the token
        user = supabase.auth.get_user(token)
        
        # Log the user info for debugging
        logger.info(f"Verified user: {user}")
        
        # Return the user data
        return {
            "sub": user.user.id,
            "email": user.user.email,
            "role": user.user.role
        }
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Token verification failed")
