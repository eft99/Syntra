from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./syntra.db"
    GEMINI_API_KEY: Optional[str] = None
    PROJECT_NAME: str = "Syntra"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8501"

    SECRET_KEY: str = Field(default="super-secret-key-change-it-in-production", description="JWT imzalama anahtarı")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7, description="Token geçerlilik süresi (dakika)")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
