from pydantic import BaseModel
from typing import List, Optional

class UserSettings(BaseModel):
    main_language: str
    learning_language: str
    language_level: str
    preferred_categories: List[str]

class UserProfile(BaseModel):
    id: int
    email: str
    username: str
    settings: Optional[UserSettings] = None