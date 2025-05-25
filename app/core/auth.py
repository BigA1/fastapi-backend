from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import requests
from typing import Optional, Dict, Any
import json
from datetime import datetime
from app.core.config import SUPABASE_URL, SUPABASE_JWT_SECRET

# Supabase JWT configuration
SUPABASE_JWT_AUD = "authenticated"
SUPABASE_JWT_ISS = f"{SUPABASE_URL}/auth/v1"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    try:
        if not SUPABASE_JWT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWT secret not configured"
            )

        # Verify the token using the JWT secret
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience=SUPABASE_JWT_AUD,
            issuer=SUPABASE_JWT_ISS
        )
        
        # Extract user ID from the token
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
            
        # Log successful authentication
        print(f"Successfully authenticated user: {user_id}")
        
        # Return user info as a dictionary
        return {
            "id": user_id,
            "email": payload.get("email"),
            "token": token  # Include the token for Supabase operations
        }
        
    except JWTError as e:
        print(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    except Exception as e:
        print(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) 