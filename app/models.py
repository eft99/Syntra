"""
app/models.py
-------------
SQLAlchemy 2.0 ORM modelleri — Mapped / mapped_column stili
"""

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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------
class Product(Base):
    """
    Ürün kaydı.
    """
    __tablename__ = "products"

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

    inventory_logs: Mapped[List["InventoryLog"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="select",
    )

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
# Order & OrderItem
# ---------------------------------------------------------------------------
class Order(Base):
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

    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Order id={self.id} number={self.order_number} customer={self.customer_name!r}>"


class OrderItem(Base):
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
    
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


# ---------------------------------------------------------------------------
# User (Auth)
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role}>"
