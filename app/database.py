from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# 1. Asenkron Motorun Kurulumu
# Bu motor, Python'un veritabanına asenkron (işleri bekletmeden)
# komutlar göndermesini sağlayan ana araçtır.

engine = create_async_engine(settings.DATABASE_URL,
                             echo=settings.DEBUG)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # İşlem sonunda hata yoksa, yapılan değişiklikleri veritabanına kaydet.
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
