"""
app/services/data_loader.py
---------------------------
Excel dosyasından ürün verilerini okuyan ve veritabanına asenkron olarak
toplu (bulk) kayıt yapan servis.
"""

import io
import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from app.database import AsyncSessionLocal
from app.models import Product

async def process_inventory_excel(file_content: bytes):
    """
    Excel dosyasını okur, verileri temizler ve veritabanına toplu olarak ekler.
    
    Beklenen Sütunlar:
    - Ürün Adı -> Product.name
    - SKU      -> Product.sku
    - Stok     -> Product.stock_count
    - Fiyat    -> Product.price
    """
    
    # 1. Pandas ile Excel dosyasını oku
    df = pd.read_excel(io.BytesIO(file_content))
    
    # 2. Sütun isimlerini eşleştir ve Türk karakter hassasiyetini yönet
    column_mapping = {
        'Ürün Adı': 'name',
        'SKU': 'sku',
        'Stok': 'stock_count',
        'Fiyat': 'price'
    }
    
    # Mevcut sütunları normalleştirerek eşleşmeyi kolaylaştır
    # (Boşlukları temizle ve eşleşenleri değiştir)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns=column_mapping)
    
    # 3. Veri Temizleme
    # - İsmi boş olan satırları sil
    df = df.dropna(subset=['name'])
    
    # - Veri tiplerini dönüştür (Hatalı verileri 0 veya varsayılan yapar)
    df['stock_count'] = pd.to_numeric(df['stock_count'], errors='coerce').fillna(0).astype(int)
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0).astype(float)
    
    # 4. Veritabanına Kayıt (Bulk Insert)
    # DataFrame'i sözlük listesine dönüştür
    data_list = df[['name', 'sku', 'stock_count', 'price']].to_dict(orient='records')
    
    if not data_list:
        return {"status": "skipped", "message": "Yüklenecek geçerli veri bulunamadı."}

    async with AsyncSessionLocal() as session:
        try:
            # PostgreSQL için insert...on_conflict_do_nothing (veya update) kullanılabilir
            # Burada kullanıcı talebi doğrultusunda doğrudan bulk insert yapıyoruz.
            stmt = insert(Product).values(data_list)
            
            # Eğer SKU çakışması varsa hiçbir şey yapma (hata almamak için)
            stmt = stmt.on_conflict_do_nothing(index_elements=['sku'])
            
            await session.execute(stmt)
            await session.commit()
            
            return {
                "status": "success",
                "processed_count": len(data_list),
                "message": f"{len(data_list)} ürün başarıyla işlendi."
            }
        except Exception as e:
            await session.rollback()
            return {"status": "error", "message": str(e)}
