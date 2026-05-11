"""
app/services/inventory_service.py
----------------------------------
Stok yönetimi, sorgu optimizasyonu ve analitik veri hesaplama servisi.
"""

from typing import List, Dict, Any
from sqlalchemy import select, func, desc
from sqlalchemy.dialects.postgresql import insert
from app.database import AsyncSessionLocal
from app.models import Product

async def get_low_stock_items(threshold: int = 10) -> List[Dict[str, Any]]:
    """
    Kritik stok seviyesinin altındaki ürünleri getirir.
    Performans için sadece gerekli kolonları seçer.
    """
    async with AsyncSessionLocal() as session:
        # Sorgu optimizasyonu: Sadece gerekli kolonları seç (SELECT id, name, sku, stock_count)
        stmt = (
            select(Product.id, Product.name, Product.sku, Product.stock_count)
            .where(Product.stock_count < threshold)
            .order_by(Product.stock_count.asc())
        )
        result = await session.execute(stmt)
        # Row nesnelerini sözlük listesine dönüştür
        return [row._asdict() for row in result.all()]

async def get_inventory_summary() -> Dict[str, Any]:
    """
    Genel stok özetini ve analitik verileri hesaplar.
    """
    async with AsyncSessionLocal() as session:
        # 1. Toplam Ürün Sayısı ve Toplam Envanter Değeri (DB-side calculation)
        summary_stmt = select(
            func.count(Product.id).label("total_products"),
            func.sum(Product.price * Product.stock_count).label("total_value")
        )
        summary_res = await session.execute(summary_stmt)
        summary = summary_res.one()

        # 2. En pahalı 5 ürün
        expensive_stmt = (
            select(Product.name, Product.price)
            .order_by(desc(Product.price))
            .limit(5)
        )
        expensive_res = await session.execute(expensive_stmt)
        top_expensive = [row._asdict() for row in expensive_res.all()]

        return {
            "total_products": summary.total_products or 0,
            "total_inventory_value": float(summary.total_value or 0),
            "top_5_expensive_items": top_expensive
        }

async def seed_test_data():
    """
    Demo için 10-15 tane gerçekçi örnek ürün ekler.
    """
    test_products = [
        {"name": "MacBook Pro 16", "sku": "LAP-001", "price": 85000.00, "stock_count": 5},
        {"name": "Gaming Monitor 27", "sku": "MON-001", "price": 12500.00, "stock_count": 12},
        {"name": "Mekanik Klavye RGB", "sku": "KBD-001", "price": 3200.00, "stock_count": 25},
        {"name": "Kablosuz Mouse", "sku": "MSE-001", "price": 1850.00, "stock_count": 8},
        {"name": "USB-C Hub 7-in-1", "sku": "ACC-001", "price": 1200.00, "stock_count": 40},
        {"name": "iPhone 15 Pro", "sku": "PHN-001", "price": 72000.00, "stock_count": 3},
        {"name": "Noise Cancelling Headphones", "sku": "AUD-001", "price": 9500.00, "stock_count": 15},
        {"name": "Laptop Standı Alüminyum", "sku": "ACC-002", "price": 850.00, "stock_count": 30},
        {"name": "External SSD 1TB", "sku": "STR-001", "price": 4200.00, "stock_count": 20},
        {"name": "Webcam 4K", "sku": "CAM-001", "price": 5400.00, "stock_count": 7},
        {"name": "Bluetooth Hoparlör", "sku": "AUD-002", "price": 2800.00, "stock_count": 18},
        {"name": "Akıllı Saat", "sku": "WCH-001", "price": 11000.00, "stock_count": 10}
    ]

    async with AsyncSessionLocal() as session:
        try:
            # SKU çakışması durumunda işlem yapma (Daha önce eklenmiş olabilirler)
            stmt = insert(Product).values(test_products).on_conflict_do_nothing(index_elements=['sku'])
            await session.execute(stmt)
            await session.commit()
            print(f"✅ {len(test_products)} test ürünü hazırlandı.")
        except Exception as e:
            await session.rollback()
            print(f"❌ Veri ekleme hatası: {e}")
