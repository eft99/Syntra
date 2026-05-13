
import asyncio
import pandas as pd
import io
from app.services.data_loader import process_inventory_excel
from app.database import engine, Base, init_db

async def test_loader():
    print("--- Veritabanı Hazırlanıyor ---")
    await init_db()
    
    print("--- Excel Loader Testi Başlatılıyor ---")
    
    # 1. Test verisi oluştur (Bellek üzerinde Excel)
    data = {
        'Ürün Adı': ['Test Ürün 1', 'Test Ürün 2', 'Geçersiz Satır'],
        'SKU': ['TST-001', 'TST-002', 'TST-999'],
        'Stok': [10, 20, 'Hatalı'],
        'Fiyat': [150.50, 200.00, 'Bedava']
    }
    df = pd.DataFrame(data)
    
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False)
    file_content = excel_buffer.getvalue()
    
    # 2. Fonksiyonu çağır
    print("Servis çağrılıyor...")
    result = await process_inventory_excel(file_content)
    
    print(f"Sonuç: {result}")
    
    if result['status'] == 'success':
        print("✅ Test Başarılı!")
    else:
        print(f"❌ Test Başarısız: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(test_loader())
