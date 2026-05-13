from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=2, max_length=50, example="SABUN-001")
    name: str = Field(..., min_length=2, max_length=200, example="Organik Lavanta Sabunu")
    stock_quantity: int = Field(ge=0)
    critical_limit: int = Field(default=10, ge=0)
    supplier_email: Optional[EmailStr] = None

    @field_validator("sku")
    @classmethod
    def sku_gecerli_olmali(cls, v: str) -> str:
        v = v.strip().upper()
        if not re.match(r"^[A-Z0-9\-]{2,50}$", v):
            raise ValueError("SKU yalnızca büyük harf, rakam ve tire içerebilir.")
        return v

    @field_validator("name")
    @classmethod
    def urun_adi_temizle(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Ürün adı en az 2 karakter olmalıdır.")
        return v


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    model_config = {"from_attributes": True}


class OrderItemBase(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=10000)


class OrderItemRead(OrderItemBase):
    id: int
    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    items: List[OrderItemBase] = Field(..., min_length=1, max_length=50)

    @field_validator("customer_name")
    @classmethod
    def musteri_adi_temizle(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Müşteri adı en az 2 karakter olmalıdır.")
        return v


class OrderRead(BaseModel):
    id: int
    order_number: str
    customer_name: str
    status: str
    created_at: datetime
    items: List[OrderItemRead]
    model_config = {"from_attributes": True}


class SupplierDraftRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(default=50, gt=0, le=10000)


class NotificationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=2000)
    channel: str = Field(default="system")

    @field_validator("channel")
    @classmethod
    def kanal_gecerli_olmali(cls, v: str) -> str:
        gecerli_kanallar = {"system", "email", "whatsapp", "telegram"}
        if v not in gecerli_kanallar:
            raise ValueError(f"Geçersiz kanal. Geçerli seçenekler: {', '.join(gecerli_kanallar)}")
        return v


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserRead(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
