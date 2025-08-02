from typing import Optional
from supabase import Client
from app.schemas.user_settings import UserSettingsCreate, UserSettingsUpdate, UserSettingsInDB
import logging

logger = logging.getLogger(__name__)

#Reviewed. finished.
async def create_user_settings(
    supabase: Client,
    user_id: str,
    settings: UserSettingsCreate
) -> UserSettingsInDB:
    """
    Create new user settings for a specific user.
    
    Args:
        supabase: Supabase client instance
        user_id: UUID of the user
        settings: UserSettingsCreate schema with settings data
        
    Returns:
        UserSettingsInDB: Created user settings
        
    Raises:
        Exception: If creation fails
    """
    try:
        # Prepare data for insertion
        settings_data = {
            "user_id": user_id,
            "main_language": settings.main_language,
            "learning_language": settings.learning_language,
            "language_level": settings.language_level,
            "preferred_categories": settings.preferred_categories or []
        }
        
        # Insert into database
        response = supabase.table("user_settings").insert(settings_data).execute()
        
        if not response.data:
            raise Exception("Failed to create user settings")
            
        return UserSettingsInDB(**response.data[0])
        
    except Exception as e:
        logger.error(f"Error creating user settings: {str(e)}")
        raise


async def get_user_settings(
    supabase: Client,
    user_id: str
) -> Optional[UserSettingsInDB]:
    """
    Retrieve user settings for a specific user.
    
    Args:
        supabase: Supabase client instance
        user_id: UUID of the user
        
    Returns:
        UserSettingsInDB: User settings if found, None otherwise
        
    Raises:
        Exception: If query fails
    """
    try:
        response = supabase.table("user_settings") \
            .select("*") \
            .eq("user_id", user_id) \
            .maybe_single() \
            .execute()
            
        if not response:
            return None
            
        return UserSettingsInDB(**response.data)
        
    except Exception as e:
        logger.error(f"Error retrieving user settings: {str(e)}")
        raise


async def update_user_settings(
    supabase: Client,
    user_id: str,
    settings_update: UserSettingsUpdate
) -> Optional[UserSettingsInDB]:
    """
    Update user settings for a specific user.
    
    Args:
        supabase: Supabase client instance
        user_id: UUID of the user
        settings_update: UserSettingsUpdate schema with fields to update
        
    Returns:
        UserSettingsInDB: Updated user settings if found, None otherwise
        
    Raises:
        Exception: If update fails
    """
    try:
        # Filter out None values
        update_data = {
            key: value for key, value in settings_update.dict(exclude_unset=True).items()
            if value is not None
        }
        
        if not update_data:
            return await get_user_settings(supabase, user_id)
        
        response = supabase.table("user_settings") \
            .update(update_data) \
            .eq("user_id", user_id) \
            .execute()
            
        if not response.data:
            return None
            
        return UserSettingsInDB(**response.data[0])
        
    except Exception as e:
        logger.error(f"Error updating user settings: {str(e)}")
        raise


async def delete_user_settings(
    supabase: Client,
    user_id: str
) -> bool:
    """
    Delete user settings for a specific user.
    
    Args:
        supabase: Supabase client instance
        user_id: UUID of the user
        
    Returns:
        bool: True if settings were deleted, False if not found
        
    Raises:
        Exception: If deletion fails
    """
    try:
        response = supabase.table("user_settings") \
            .delete() \
            .eq("user_id", user_id) \
            .execute()
            
        return bool(response.data)
        
    except Exception as e:
        logger.error(f"Error deleting user settings: {str(e)}")
        raise


async def ensure_user_settings_exists(
    supabase: Client,
    user_id: str
) -> UserSettingsInDB:
    """
    Ensure user settings exist for a user, creating default if necessary.
    
    Args:
        supabase: Supabase client instance
        user_id: UUID of the user
        
    Returns:
        UserSettingsInDB: User settings (existing or newly created)
    """
    existing = await get_user_settings(supabase, user_id)
    if existing:
        return existing
    
    # Create default settings
    default_settings = UserSettingsCreate(
        main_language="English",
        learning_language="Spanish",
        language_level="Beginner (A1)",
        preferred_categories=[]
    )
    
    return await create_user_settings(supabase, user_id, default_settings)