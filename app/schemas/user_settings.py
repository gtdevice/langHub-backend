from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class UserSettingsBase(BaseModel):
    """Base schema for user settings with common fields."""
    main_language: Optional[str] = Field(None, description="User's native language")
    learning_language: Optional[str] = Field(None, description="Target language for learning")
    language_level: Optional[str] = Field(None, description="Proficiency level (e.g., A1, A2, B1, B2, C1, C2)")
    preferred_categories: Optional[List[str]] = Field(
        default_factory=list,
        description="List of preferred article categories"
    )


class UserSettingsCreate(UserSettingsBase):
    """Schema for creating new user settings."""
    main_language: str = Field(..., description="User's native language")
    learning_language: str = Field(..., description="Target language for learning")
    language_level: str = Field(..., description="Proficiency level")


class UserSettingsUpdate(UserSettingsBase):
    """Schema for updating existing user settings."""
    pass


class UserSettingsResponse(UserSettingsBase):
    """Schema for user settings API responses."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSettingsInDB(UserSettingsBase):
    """Schema for user settings as stored in database."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True