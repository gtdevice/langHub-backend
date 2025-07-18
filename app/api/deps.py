from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from app.core.config import settings
import jwt
from typing import Dict, Any


security = HTTPBearer()


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)


async def get_current_user_supabase_client(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Client:
    """
    This is the core security dependency. It does two things:
    1. Validates the JWT from the Authorization header.
    2. If valid, it returns a NEW Supabase client instance that is
       authenticated AS THE USER who made the request.

    This ensures all subsequent database calls made with this client
    will respect your Row Level Security policies.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    token = credentials.credentials
    try:
        # Step 1: Decode and validate the JWT
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )

        # The 'sub' claim in the JWT is the user's unique ID
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")

        # Step 2: Set the authentication context for the admin client
        # This tells the Supabase client to act on behalf of the user for the next request.
        # It effectively "impersonates" the user using their validated JWT.
        supabase_admin = create_client(settings.supabase_url, settings.supabase_anon_key)
        supabase_admin.auth.set_session(access_token=token, refresh_token=token)

        # We return the admin client instance, now configured to act as the user.
        return supabase_admin

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {e}")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """
    Extract JWT token from Authorization header and validate it using Supabase.
    Returns the user object if valid, raises HTTPException if invalid.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    token = credentials.credentials
    
    try:
        # Decode JWT token using Supabase JWT secret
        payload = jwt.decode(
            token, 
            settings.supabase_jwt_secret, 
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        # Extract user ID from payload
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        # Get user from Supabase
        response = supabase.auth.get_user(token)
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return response.user.model_dump()
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
