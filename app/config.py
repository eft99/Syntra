from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ortam değişkenleri (.env); yerel geliştirme için güvenli varsayılanlar."""

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://admin:secret_password@127.0.0.1:5432/kobi_os",
        description="Async SQLAlchemy veritabanı URL'i",
    )
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API anahtarı (AI uçları için)")

    PROJECT_NAME: str = "Syntra"
    DEBUG: bool = False
    # CORS: virgülle ayrılmış kökenler veya tek başına *
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:8501,http://127.0.0.1:8501,http://localhost:3000,*",
        description="İzin verilen tarayıcı kökenleri (CSV)",
    )

    SECRET_KEY: str = Field(default="super-secret-key-change-it-in-production", description="JWT imzalama anahtarı")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7, description="Token geçerlilik süresi (dakika)")


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
