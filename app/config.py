import os

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Bu class, .env dosyasındaki ortam değişkenlerini okur ve
    kod içinde tip güvenli bir şekilde kullanmamızı sağlar
    """

    # Veritabanı bağlantı adresi ve anahtarı (.env dosyasından çekilecek)
    DATABASE_URL: str

    # Google Gemini yapay zeka anahtarı (.env dosyasından çekilecek)
    GEMINI_API_KEY: str

    # Projemizin adı (.env dosyasından çekilecek)
    PROJECT_NAME: str = "Syntra"

    # Debug (hata ayıklama) modu (.env dosyasından çekilecek)
    DEBUG: bool = False

    # Bu ayar, pydantic'e ".env" dosyasını otomatik olarak aramasını söyler.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Ayarları kullanabilmek için sınıfı bir değişkene atıyoruz.
# Projemizin her yerinde bu 'settings' değişkenini kullanacağız.
settings = Settings()
