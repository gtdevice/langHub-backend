from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from app.core.config import settings
import jwt
from typing import Dict, Any


security = HTTPBearer()


class AuthenticatedUser:
    """Unified dependency class that provides both user information and authenticated Supabase client."""
    
    def __init__(self, user_id: str, user_data: Dict[str, Any], client: Client):
        self.user_id = user_id
        self.user_data = user_data
        self.client = client


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)


async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthenticatedUser:
    """
    Unified dependency that validates JWT and returns both user info and authenticated client.
    
    This eliminates the need for dual dependencies (get_current_user + get_current_user_supabase_client)
    by providing both user_id and authenticated client in a single call.
    
    Returns:
        AuthenticatedUser: Object containing user_id, user_data, and authenticated Supabase client
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    token = credentials.credentials
    try:
        # Step 1: Decode and validate JWT
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")

        # Step 2: Create authenticated client
        supabase_client = create_client(settings.supabase_url, settings.supabase_anon_key)
        supabase_client.auth.set_session(access_token=token, refresh_token=token)

        # Step 3: Get user data from Supabase
        response = supabase_client.auth.get_user(token)
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        user_data = response.user.model_dump()
        
        return AuthenticatedUser(
            user_id=user_id,
            user_data=user_data,
            client=supabase_client
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {e}")


# Legacy dependencies - kept for backward compatibility
async def get_current_user_supabase_client(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Client:
    """Legacy dependency - use get_authenticated_user instead."""
    auth_user = await get_authenticated_user(credentials)
    return auth_user.client


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Legacy dependency - use get_authenticated_user instead."""
    auth_user = await get_authenticated_user(credentials)
    return auth_user.user_data
