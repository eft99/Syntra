from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base
from typing import List


class Product(Base):
    """KOBİ'nin stoklarını tuttuğumuz Ürünler rafı (tablosu)."""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # Benzersiz Ürün Kodu
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    critical_limit: Mapped[int] = mapped_column(Integer, default=10)  # AI bu sınırı izleyecek
    supplier_email: Mapped[str] = mapped_column(String(100), nullable=True)

    # Bir ürünün birden fazla sipariş detayı olabilir.
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")


class Order(Base):
    """Müşteri siparişlerinin ana bilgilerini tutan raf (tablo)."""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Bekliyor")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Bir siparişin içinde birden fazla ürün detayı olabilir.
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Hangi siparişte hangi üründen kaç adet olduğunu tutan ara raf (tablo)."""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)

    # Bu detayların hangi siparişe ve hangi ürüne ait olduğunu belirtiyoruz.
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")