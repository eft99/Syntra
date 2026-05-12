import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api.endpoints import router
from app.api.demo import router as demo_router

logger = logging.getLogger(__name__)

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
        "description": "⚡ Jüri sunumu için hızlı veri yükleme ve sıfırlama araçları.",
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
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    contact={
        "name": "Syntra Ekibi",
    },
)

origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]

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