import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Order, OrderItem, Product

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/demo", tags=["Demo"])

ORNEK_URUNLER = [
    {"sku": "SABUN-001", "name": "Organik Lavanta Sabunu", "stock_quantity": 150, "critical_limit": 20, "supplier_email": "lavanta@tedarik.com"},
    {"sku": "KAHVE-002", "name": "Türk Kahvesi 500g", "stock_quantity": 8, "critical_limit": 15, "supplier_email": "kahve@tedarik.com"},
    {"sku": "CAY-003", "name": "Karadeniz Çayı 1kg", "stock_quantity": 5, "critical_limit": 10, "supplier_email": "cay@tedarik.com"},
    {"sku": "ZEY-004", "name": "Sızma Zeytinyağı 1L", "stock_quantity": 42, "critical_limit": 10, "supplier_email": "zeytinyagi@tedarik.com"},
    {"sku": "BAL-005", "name": "Doğal Çiçek Balı 500g", "stock_quantity": 3, "critical_limit": 5, "supplier_email": "bal@tedarik.com"},
]


@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_demo_data(db: AsyncSession = Depends(get_db)):
    eklenen = 0
    for veri in ORNEK_URUNLER:
        mevcut = (await db.execute(select(Product).where(Product.sku == veri["sku"]))).scalar_one_or_none()
        if not mevcut:
            db.add(Product(**veri))
            eklenen += 1

    await db.flush()
    logger.info("Demo verisi yuklendi: %d urun eklendi.", eklenen)

    return {
        "durum": "basarili",
        "mesaj": f"{eklenen} yeni ürün eklendi. Mevcut ürünler atlandı.",
        "toplam_tanimli_urun": len(ORNEK_URUNLER),
    }


@router.delete("/reset", status_code=status.HTTP_200_OK)
async def reset_demo_data(
    onayla: str = Query(..., description="Silme işlemini onaylamak için 'evet' yazın."),
    db: AsyncSession = Depends(get_db),
):
    if onayla.strip().lower() != "evet":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Silme işlemi onaylanmadı. Devam etmek için 'onayla=evet' gönderin.",
        )
    await db.execute(delete(OrderItem))
    await db.execute(delete(Order))
    await db.execute(delete(Product))
    await db.flush()
    logger.warning("Demo sifirlama yapildi: tum urun ve siparis kayitlari silindi.")

    return {
        "durum": "sifirlandi",
        "mesaj": "Tüm ürün ve sipariş kayıtları temizlendi.",
    }


@router.get("/status", tags=["Demo"])
async def demo_status(db: AsyncSession = Depends(get_db)):
    urun_sayisi = (await db.execute(select(func.count()).select_from(Product))).scalar()
    siparis_sayisi = (await db.execute(select(func.count()).select_from(Order))).scalar()
    kritik_sayisi = (await db.execute(
        select(func.count()).select_from(Product).where(Product.stock_quantity <= Product.critical_limit)
    )).scalar()

    return {
        "sistemde_kayitli_urun": urun_sayisi,
        "toplam_siparis": siparis_sayisi,
        "kritik_stok_urun_sayisi": kritik_sayisi,
        "demo_hazir": urun_sayisi > 0,
        "mesaj": "Demo hazır, jüriye gösterebilirsiniz." if urun_sayisi > 0 else "Önce /api/demo/seed adresini çağırın.",
    }
