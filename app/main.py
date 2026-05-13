from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.api import endpoints


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Bu fonksiyon, uygulama başladığında ve kapandığında çalışacak kodları yönetir.
    Örneğin, veritabanı bağlantılarını açmak ve kapamak için ideal bir yerdir.
    """
    print(f"🚀 {settings.PROJECT_NAME} uygulaması başlatılıyor...")
    yield
    print("🛑 Uygulama kapatılıyor...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(endpoints.router)

@app.get("/health", tags=["System"])
async def health_check():
    """
    Bu basit endpoint, Docker'ın uygulamamızın 'canlı' olup olmadığını
    kontrol etmesi için kullanılır. Sistemin sağlığını kontrol eder.
    """
    return {"status": "ok", "app_name": settings.PROJECT_NAME}