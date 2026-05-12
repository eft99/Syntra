from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- ÜRÜN ŞEMALARI ---

class ProductBase(BaseModel):
    """Bir ürünün temel alanlarını tanımlayan şema."""
    sku: str = Field(..., description="Benzersiz Ürün Kodu", example="SABUN-001")
    name: str = Field(..., description="Ürünün tam adı", example="Organik Lavanta Sabunu")
    stock_quantity: int = Field(ge=0, description="Stok miktarı, 0'dan küçük olamaz.")
    critical_limit: int = Field(default=10, description="AI uyarısı için kritik stok seviyesi.")
    price: float = Field(default=0.0, description="Birim fiyat (TL)")
    category: Optional[str] = Field(None, description="Ürün kategorisi")
    supplier_email: Optional[str] = Field(None, description="Tedarikçinin e-posta adresi.")

class ProductCreate(ProductBase):
    """Yeni bir ürün oluştururken kullanılacak şema. Temel alanları miras alır."""
    pass

class ProductRead(ProductBase):
    """Veritabanından bir ürün okunduğunda kullanıcıya gösterilecek şema."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        # Bu ayar, SQLAlchemy model nesnelerini otomatik olarak
        # Pydantic şemasına dönüştürmemizi sağlar.
        from_attributes = True

# --- SİPARİŞ ÖĞESİ (ORDER ITEM) ŞEMALARI ---

class OrderItemBase(BaseModel):
    """Bir siparişin içindeki tek bir ürün kaleminin temel şeması."""
    product_id: int
    quantity: int = Field(gt=0, description="Miktar 0'dan büyük olmalı.")

class OrderItemRead(OrderItemBase):
    """Okuma işlemi için sipariş kalemi şeması."""
    id: int
    class Config:
        from_attributes = True

# --- SİPARİŞ ŞEMALARI ---

class OrderCreate(BaseModel):
    """Yeni bir sipariş oluşturmak için gereken verileri tanımlayan şema."""
    customer_name: str
    items: List[OrderItemBase] # Siparişin içinde birden fazla ürün kalemi olabilir.

class OrderRead(BaseModel):
    """Veritabanından okunan bir siparişin kullanıcıya gösterilecek hali."""
    id: int
    order_number: str
    customer_name: str
    status: str
    created_at: datetime
    items: List[OrderItemRead]

    class Config:
        from_attributes = True