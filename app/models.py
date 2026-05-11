"""
app/models.py
-------------
SQLAlchemy 2.0 ORM modelleri — Mapped / mapped_column stili

Tablolar:
  products       — Ürün kataloğu
  inventory_logs — Stok hareket günlüğü
"""

import uuid
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
    id          : UUID birincil anahtar (veritabanı tarafından üretilir)
    name        : Ürün adı (zorunlu, 200 karakter)
    sku         : Benzersiz stok kodu — Stock Keeping Unit (50 karakter)
    stock_count : Anlık stok miktarı (varsayılan 0)
    price       : Birim fiyat — NUMERIC(12,2) ile kuruş hassasiyeti
    category    : Ürün kategorisi (isteğe bağlı, 100 karakter)
    created_at  : Kayıt oluşturma zamanı (sunucu tarafı, UTC)
    updated_at  : Son güncelleme zamanı (otomatik güncellenir, UTC)
    """

    __tablename__ = "products"

    # Birincil anahtar — PostgreSQL'in native uuid tipini kullan
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
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

    stock_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Anlık stok miktarı",
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

    def __repr__(self) -> str:
        return f"<Product id={self.id!s:.8} sku={self.sku} name={self.name!r}>"


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
    product_id    : İlgili ürünün UUID'si (products.id FK)
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

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
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
            f"<InventoryLog id={self.id} product_id={self.product_id!s:.8}"
            f" change={sign}{self.change_amount}>"
        )