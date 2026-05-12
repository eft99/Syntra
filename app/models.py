"""
app/models.py
-------------
SQLAlchemy 2.0 ORM modelleri — Mapped / mapped_column stili

Tablolar:
  products       — Ürün kataloğu
  inventory_logs — Stok hareket günlüğü
"""

import uuid
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------
class Product(Base):
    """
    Ürün kaydı.

    Kolonlar
    --------
    id               : Tamsayı birincil anahtar (otomatik artan)
    name             : Ürün adı (zorunlu, 200 karakter)
    sku              : Benzersiz stok kodu — Stock Keeping Unit (50 karakter)
    stock_quantity   : Anlık stok miktarı (varsayılan 0)
    critical_limit   : Kritik stok seviyesi (varsayılan 10)
    supplier_email   : Tedarikçi e-posta adresi (isteğe bağlı)
    price            : Birim fiyat — NUMERIC(12,2) ile kuruş hassasiyeti
    category         : Ürün kategorisi (isteğe bağlı, 100 karakter)
    created_at       : Kayıt oluşturma zamanı (sunucu tarafı, UTC)
    updated_at       : Son güncelleme zamanı (otomatik güncellenir, UTC)
    """

    __tablename__ = "products"

    # Birincil anahtar — Integer (Autoincrement)
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)

    sku: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Stock Keeping Unit — benzersiz ürün kodu",
    )

    stock_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Anlık stok miktarı",
    )

    critical_limit: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
        comment="Kritik stok seviyesi (AI uyarısı için)",
    )

    supplier_email: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Tedarikçi e-posta adresi",
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Birim fiyat (TL)",
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Ürün kategorisi (elektronik, gıda vb.)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # İlişki: bir ürüne ait tüm stok hareketleri
    inventory_logs: Mapped[List["InventoryLog"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # İlişki: bir ürüne ait tüm sipariş kalemleri
    order_items: Mapped[List["OrderItem"]] = relationship(
        back_populates="product",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} sku={self.sku} name={self.name!r}>"


# ---------------------------------------------------------------------------
# InventoryLog
# ---------------------------------------------------------------------------
class InventoryLog(Base):
    """
    Stok hareket günlüğü.

    Her stok değişikliğinde (giriş/çıkış/düzeltme) bir kayıt oluşturulur.

    Kolonlar
    --------
    id            : Otomatik artan tamsayı birincil anahtar
    product_id    : İlgili ürünün ID'si (products.id FK)
    change_amount : Değişim miktarı — pozitif=giriş, negatif=çıkış
    reason        : Hareket nedeni (max 500 karakter, isteğe bağlı açıklama)
    timestamp     : Hareketin gerçekleştiği zaman (UTC, veritabanı varsayılanı)
    """

    __tablename__ = "inventory_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    change_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Pozitif: stok girişi | Negatif: stok çıkışı",
    )

    reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Hareket nedeni: 'Satış', 'İade', 'Sayım Düzeltmesi' vb.",
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="Hareketin UTC zamanı",
    )

    # İlişki: bu log kaydının ait olduğu ürün
    product: Mapped["Product"] = relationship(
        back_populates="inventory_logs",
        lazy="select",
    )

    def __repr__(self) -> str:
        sign = "+" if self.change_amount >= 0 else ""
        return (
            f"<InventoryLog id={self.id} product_id={self.product_id}"
            f" change={sign}{self.change_amount}>"
        )


# ---------------------------------------------------------------------------
# Order & OrderItem (Şüheda'nın API'ları için)
# ---------------------------------------------------------------------------

class Order(Base):
    """
    Müşteri siparişi.
    """
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # İlişki: siparişteki kalemler
    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Order id={self.id} number={self.order_number} customer={self.customer_name!r}>"


class OrderItem(Base):
    """
    Sipariş içindeki ürün kalemleri.
    """
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # İlişkiler
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")

    def __repr__(self) -> str:
        return f"<OrderItem id={self.id} order_id={self.order_id} product_id={self.product_id} qty={self.quantity}>"