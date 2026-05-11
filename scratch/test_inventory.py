
import asyncio
from app.services.inventory_service import seed_test_data, get_low_stock_items, get_inventory_summary
from app.database import init_db

async def run_analytics_test():
    print("--- Veritabanı Hazırlanıyor ---")
    await init_db()
    
    print("\n--- Test Verileri Ekleniyor ---")
    await seed_test_data()
    
    print("\n--- Kritik Stok Analizi (Eşik: 10) ---")
    low_stock = await get_low_stock_items(threshold=10)
    for item in low_stock:
        print(f"⚠️ Düşük Stok: {item['name']} (SKU: {item['sku']}) - Adet: {item['stock_count']}")
    
    print("\n--- Genel Envanter Özeti ---")
    summary = await get_inventory_summary()
    print(f"📊 Toplam Ürün Sayısı: {summary['total_products']}")
    print(f"💰 Toplam Envanter Değeri: {summary['total_inventory_value']:,.2f} TL")
    
    print("\n--- En Değerli 5 Ürün ---")
    for idx, item in enumerate(summary['top_5_expensive_items'], 1):
        print(f"{idx}. {item['name']}: {item['price']:,.2f} TL")

if __name__ == "__main__":
    asyncio.run(run_analytics_test())
