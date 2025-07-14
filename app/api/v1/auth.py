from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.api.deps import get_supabase_client
from app.schemas.auth import SignInRequest, SignInResponse
from gotrue.errors import AuthApiError

router = APIRouter()


@router.post("/signin", response_model=SignInResponse)
async def sign_in(
    credentials: SignInRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Sign in user with email and password.
    Returns access token and user information.
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not response.user or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        return SignInResponse(
            access_token=response.session.access_token,
            user=response.user.model_dump(),
            expires_in=response.session.expires_in or 3600
        )
        
    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        ) 