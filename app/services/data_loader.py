"""
app/services/data_loader.py
---------------------------
Excel dosyasından ürün verilerini okuyan ve veritabanına asenkron olarak
toplu (bulk) kayıt yapan servis.
"""

import io
import pandas as pd
import logging
from sqlalchemy.dialects.postgresql import insert
from app.database import AsyncSessionLocal
from app.models import Product

# Logger yapılandırması
logger = logging.getLogger(__name__)

async def process_inventory_excel(file_content: bytes):
    """
    Excel dosyasını okur, verileri temizler ve veritabanına toplu olarak ekler.
    
    Beklenen Sütunlar:
    - Ürün Adı -> Product.name
    - SKU      -> Product.sku
    - Stok     -> Product.stock_quantity
    - Fiyat    -> Product.price
    """
    
    # 1. Pandas ile Excel dosyasını oku
    try:
        df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
    except Exception as e:
        logger.error(f"Excel okuma hatası: {e}")
        return {"status": "error", "message": "Excel dosyası okunamadı. Lütfen dosya formatını kontrol edin."}
    
    # 2. Sütun isimlerini eşleştir ve Türk karakter hassasiyetini yönet
    column_mapping = {
        'Ürün Adı': 'name',
        'SKU': 'sku',
        'Stok': 'stock_quantity',
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
    df['stock_quantity'] = pd.to_numeric(df['stock_quantity'], errors='coerce').fillna(0).astype(int)
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0).astype(float)
    
    # 4. Veritabanına Kayıt (Bulk Insert)
    # DataFrame'i sözlük listesine dönüştür
    data_list = df[['name', 'sku', 'stock_quantity', 'price']].to_dict(orient='records')
    
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
            logger.error(f"Veritabanı kayıt hatası: {e}")
            return {"status": "error", "message": "Veritabanına kayıt sırasında bir hata oluştu."}
