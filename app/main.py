import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.demo import router as demo_router
from app.api.endpoints import router
from app.config import settings
from app.database import Base, engine, AsyncSessionLocal
from app.models import User
from app.services.auth_service import get_password_hash
from sqlalchemy import select

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

tags_metadata = [
    {
        "name": "Ürünler",
        "description": "Ürün listeleme, arama ve ekleme işlemleri.",
    },
    {
        "name": "Excel",
        "description": "Toplu ürün yükleme ve şablon indirme işlemleri.",
    },
    {
        "name": "Siparişler",
        "description": "Sipariş oluşturma ve listeleme. Stok otomatik düşülür.",
    },
    {
        "name": "Yapay Zeka",
        "description": "Kritik stok analizi ve tedarikçi e-posta taslağı üretimi.",
    },
    {
        "name": "Bildirimler",
        "description": "Sistem, e-posta, WhatsApp ve Telegram kanallarına bildirim gönderme.",
    },
    {
        "name": "Operasyon",
        "description": "Stok ve sipariş durumunun tek bakışta özeti.",
    },
    {
        "name": "Demo",
        "description": "Jüri sunumu için hızlı veri yükleme ve sıfırlama araçları.",
    },
    {
        "name": "Auth",
        "description": "Kimlik ve şifre sıfırlama (demo).",
    },
    {
        "name": "System",
        "description": "Servis sağlık kontrolü.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Syntra API baslatildi. Tablolar hazirlandi.")
    
    # Otomatik Admin Oluşturma
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        if not result.scalar_one_or_none():
            admin_user = User(
                username="admin",
                email="admin@syntra.app",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
            session.add(admin_user)
            await session.commit()
            logger.info("Varsayilan admin kullanicisi olusturuldu: admin / admin123")
    yield
    logger.info("Syntra API kapatildi.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "**Syntra** — KOBİ'ler için yapay zeka destekli operasyon yönetim platformu.\n\n"
        "Stok takibi, sipariş yönetimi ve tedarikçi iletişimini tek çatı altında toplar. "
        "Kritik stok seviyelerinde otomatik uyarı üretir ve e-posta taslağı hazırlar.\n\n"
        "> Demo için önce `/api/demo/seed` endpoint'ini çağırarak sistemi verilerle doldurun."
    ),
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    contact={
        "name": "Syntra Ekibi",
    },
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(router, prefix="/api")
app.include_router(demo_router, prefix="/api")


@app.get("/health", tags=["System"])
async def health_check():
    return {"durum": "basarili", "uygulama": settings.PROJECT_NAME, "versiyon": "1.0.0"}
