from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=2, max_length=50, example="SABUN-001")
    name: str = Field(..., min_length=2, max_length=200, example="Organik Lavanta Sabunu")
    stock_quantity: int = Field(ge=0)
    critical_limit: int = Field(default=10, ge=0)
    supplier_email: Optional[EmailStr] = None


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    model_config = {"from_attributes": True}


class OrderItemBase(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderItemRead(OrderItemBase):
    id: int
    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    items: List[OrderItemBase] = Field(..., min_length=1)


class OrderRead(BaseModel):
    id: int
    order_number: str
    customer_name: str
    status: str
    created_at: datetime
    items: List[OrderItemRead]
    model_config = {"from_attributes": True}