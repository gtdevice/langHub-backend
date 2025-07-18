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

    # OpenRouter Configuration
    openrouter_api_base: str = "https://openrouter.ai/api/v1"
    openrouter_api_key: str
    openrouter_model_name: str
    
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
