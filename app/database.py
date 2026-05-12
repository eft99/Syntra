"""
app/database.py
---------------
Asenkron PostgreSQL bağlantısı — SQLAlchemy 2.0 + asyncpg

Bağlantı adresinin formatı:
    postgresql+asyncpg://user:password@host:port/dbname
Bu değer .env dosyasındaki DATABASE_URL değişkeninden çekilir.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# ---------------------------------------------------------------------------
# Engine — asyncpg sürücüsüyle asenkron bağlantı havuzu
# ---------------------------------------------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,        # DEBUG=True iken SQL sorgularını loglar
    future=True,                # SQLAlchemy 2.0 davranış modu
    pool_size=10,               # Havuzdaki kalıcı bağlantı sayısı
    max_overflow=20,            # Yük altında açılabilecek ek bağlantı sayısı
    pool_pre_ping=True,         # Her kullanımda bağlantının sağlığını kontrol eder
    pool_recycle=1800,          # 30 dk'da bir bağlantıları yenile (timeout'u önler)
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,     # commit sonrası lazy-load hatalarını önler
    autoflush=False,            # elle flush kontrolü için
    autocommit=False,
)


# ---------------------------------------------------------------------------
# Deklaratif base — tüm modeller bu sınıftan türetilir
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    """Tüm ORM modellerinin ortak atası."""
    pass


# ---------------------------------------------------------------------------
# FastAPI dependency — request ömrüyle sınırlı oturum
# ---------------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI endpoint'lerinde Depends(get_db) ile kullanılır.

    Örnek::

        @router.get("/products")
        async def list_products(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Yardımcı — uygulama başlangıcında tabloları oluşturur (geliştirme ortamı)
# ---------------------------------------------------------------------------
async def init_db() -> None:
    """
    Tüm tabloları yoksa oluşturur.
    Üretim ortamında bunun yerine Alembic migration kullanın.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
