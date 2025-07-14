from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase Configuration
    supabase_url: str
    supabase_anon_key: str
    supabase_jwt_secret: str
    project_name: str
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    
    
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
