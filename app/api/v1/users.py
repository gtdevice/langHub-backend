from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return {
        "user": current_user
    }


@router.get("/profile")
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get user profile information.
    """
    return {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "created_at": current_user.get("created_at"),
        "updated_at": current_user.get("updated_at")
    } 