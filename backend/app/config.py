# إعدادات المنصة - Memorix
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# مسار مجلد backend دائماً
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""

    # Gemini
    gemini_api_key: str = ""

    # JWT
    jwt_secret_key: str = "memorix-default-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 ساعة

    # المنصة
    allowed_email_domain: str = "morix.tech"
    app_name: str = "Morix"
    app_version: str = "1.0.0"

    # CORS
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = str(BASE_DIR / ".env")
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
