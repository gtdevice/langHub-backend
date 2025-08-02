from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_authenticated_user
from app.schemas.user_settings import (
    UserSettingsCreate,
    UserSettingsUpdate,
    UserSettingsResponse
)
from app.services import user_settings as user_settings_service

router = APIRouter()
#Reviewed. finished.
@router.post(
    "/settings",
    response_model=UserSettingsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user settings",
    description="Create new user settings for the authenticated user"
)
async def create_user_settings(
        settings: UserSettingsCreate,
        auth_user = Depends(get_authenticated_user)
) -> UserSettingsResponse:
    """
    Create new user settings for the authenticated user.

    Args:
        settings: User settings data

    Returns:
        UserSettingsResponse: Created user settings

    Raises:
        HTTPException: If settings already exist or creation fails
        :param settings:
        :param auth_user:
    """
    try:
        # Check if settings already exist
        existing = await user_settings_service.get_user_settings(
            auth_user.client,
            auth_user.user_id
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User settings already exist"
            )

        # Create new settings
        new_settings = await user_settings_service.create_user_settings(
            auth_user.client,
            auth_user.user_id,
            settings
        )

        return UserSettingsResponse(**new_settings.dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user settings: {str(e)}"
        )


@router.get(
    "/settings",
    response_model=UserSettingsResponse,
    summary="Get current user settings",
    description="Retrieve the authenticated user's settings"
)
async def get_current_user_settings(
        auth_user = Depends(get_authenticated_user)
) -> UserSettingsResponse:
    """
    Get the current authenticated user's settings.

    Returns:
        UserSettingsResponse: User settings

    Raises:
        HTTPException: If settings not found
    """
    try:
        settings = await user_settings_service.get_user_settings(
            auth_user.client,
            auth_user.user_id
        )

        if not settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User settings not found"
            )

        return UserSettingsResponse(**settings.dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user settings: {str(e)}"
        )


@router.put(
    "/settings",
    response_model=UserSettingsResponse,
    summary="Update current user settings",
    description="Update the authenticated user's settings"
)
async def update_current_user_settings(
        settings_update: UserSettingsUpdate,
        auth_user = Depends(get_authenticated_user)
) -> UserSettingsResponse:
    """
    Update the current authenticated user's settings.

    Args:

    Returns:
        UserSettingsResponse: Updated user settings

    Raises:
        HTTPException: If settings not found or update fails
    """
    try:
        updated_settings = await user_settings_service.update_user_settings(
            auth_user.client,
            auth_user.user_id,
            settings_update
        )

        if not updated_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User settings not found"
            )

        return UserSettingsResponse(**updated_settings.dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user settings: {str(e)}"
        )


@router.delete(
    "/settings",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user settings",
    description="Delete the authenticated user's settings"
)
async def delete_current_user_settings(
        auth_user = Depends(get_authenticated_user)
) -> None:
    """
    Delete the current authenticated user's settings.

    Raises:
        HTTPException: If deletion fails
    """
    try:
        deleted = await user_settings_service.delete_user_settings(
            auth_user.client,
            auth_user.user_id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User settings not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user settings: {str(e)}"
        )