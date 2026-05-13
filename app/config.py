from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    DATABASE_URL: str
    GEMINI_API_KEY: str
    PROJECT_NAME: str = "Syntra"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @field_validator("GEMINI_API_KEY")
    @classmethod
    def api_key_must_exist(cls, v: str) -> str:
        if not v or v == "your_gemini_api_key_here":
            raise ValueError("Geçerli bir GEMINI_API_KEY girilmeli")
        return v

    SECRET_KEY: str = Field(default="super-secret-key-change-it-in-production", description="JWT imzalama anahtarı")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7, description="Token geçerlilik süresi (dakika)")


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
