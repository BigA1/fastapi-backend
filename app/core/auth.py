from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.supabase.client import get_authenticated_client
from app.core.config import settings
from jose import jwt, JWTError
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Validate the JWT token and return the user information.
    """
    try:
        logger.info("Auth middleware: Starting token validation")
        logger.info(f"Auth middleware: Token (first 20 chars): {credentials.credentials[:20]}...")
        
        token = credentials.credentials
        supabase = get_authenticated_client(token)
        logger.info("Auth middleware: Created authenticated client")
        
        # Verify the token with Supabase
        try:
            user = supabase.auth.get_user(token)
            logger.info(f"Auth middleware: User verification successful: {user}")
        except Exception as e:
            logger.error(f"Auth middleware: Error verifying user: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user:
            logger.error("Auth middleware: Token is invalid or user not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Auth middleware: Token validated for user_id: {user.user.id}")
        # Return a dictionary with user data and token
        return {
            "id": user.user.id,
            "email": user.user.email,
            "token": token
        }
        
    except jwt.ExpiredSignatureError:
        logger.error("Auth middleware: Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.error(f"Auth middleware: JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Auth middleware: Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) 