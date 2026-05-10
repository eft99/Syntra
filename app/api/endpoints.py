import io
import uuid
from typing import List, Literal, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Order, OrderItem, Product
from app.schemas import OrderCreate, OrderRead, ProductCreate, ProductRead

router = APIRouter()

ALLOWED_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# ── Products ─────────────────────────────────

@router.get("/products", response_model=List[ProductRead], tags=["Products"])
async def list_products(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/products/{product_id}", response_model=ProductRead, tags=["Products"])
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Ürün bulunamadı: ID={product_id}")
    return product


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED, tags=["Products"])
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Product).where(Product.sku == data.sku))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, detail=f"Bu SKU zaten kayıtlı: {data.sku}")
    product = Product(**data.model_dump())
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product


# ── Excel ────────────────────────────────────

@router.get("/download-template", tags=["Excel"])
async def download_template():
    df = pd.DataFrame([
        {"sku": "SABUN-001", "name": "Organik Lavanta Sabunu", "stock_quantity": 150, "critical_limit": 20, "supplier_email": "tedarikci@example.com"},
        {"sku": "KAHVE-002", "name": "Türk Kahvesi 500g", "stock_quantity": 8, "critical_limit": 15, "supplier_email": "kahve@example.com"},
    ])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Ürünler")
    output.seek(0)
    return StreamingResponse(
        output,
        media_type=ALLOWED_MIME,
        headers={"Content-Disposition": "attachment; filename=syntra_urun_sablonu.xlsx"},
    )


@router.post("/upload-products", tags=["Excel"])
async def upload_products(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")) or file.content_type not in (
        ALLOWED_MIME,
        "application/vnd.ms-excel",
    ):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Sadece .xlsx veya .xls dosyaları kabul edilir.")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Dosya boyutu 5MB'ı geçemez.")

    try:
        df = pd.read_excel(io.BytesIO(content))
    except Exception:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Excel dosyası okunamadı.")

    if not {"sku", "name", "stock_quantity"}.issubset(df.columns):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Zorunlu sütunlar eksik: sku, name, stock_quantity")

    df = df.where(pd.notna(df), None)
    added, updated, errors = 0, 0, []

    for idx, row in df.iterrows():
        try:
            sku = str(row["sku"]).strip()
            if not sku:
                raise ValueError("SKU boş olamaz")
            result = await db.execute(select(Product).where(Product.sku == sku))
            existing = result.scalar_one_or_none()
            if existing:
                existing.name = str(row["name"])
                existing.stock_quantity = int(row["stock_quantity"])
                existing.critical_limit = int(row.get("critical_limit") or 10)
                existing.supplier_email = row.get("supplier_email")
                updated += 1
            else:
                db.add(Product(
                    sku=sku,
                    name=str(row["name"]),
                    stock_quantity=int(row["stock_quantity"]),
                    critical_limit=int(row.get("critical_limit") or 10),
                    supplier_email=row.get("supplier_email"),
                ))
                added += 1
        except Exception as e:
            errors.append({"satir": int(idx) + 2, "hata": str(e)})

    return {"eklenen": added, "guncellenen": updated, "hatalar": errors}


# ── Orders ───────────────────────────────────

@router.get("/orders", response_model=List[OrderRead], tags=["Orders"])
async def list_orders(status_filter: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Order).options(selectinload(Order.items))
    if status_filter:
        query = query.where(Order.status == status_filter)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED, tags=["Orders"])
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_db)):
    order = Order(order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}", customer_name=data.customer_name)
    db.add(order)
    await db.flush()

    for item in data.items:
        result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Ürün bulunamadı: ID={item.product_id}")
        if product.stock_quantity < item.quantity:
            raise HTTPException(status.HTTP_409_CONFLICT, detail=f"Yetersiz stok: {product.name} (mevcut: {product.stock_quantity})")
        product.stock_quantity -= item.quantity
        db.add(OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity))

    await db.flush()
    result = await db.execute(select(Order).options(selectinload(Order.items)).where(Order.id == order.id))
    return result.scalar_one()


# ── AI ───────────────────────────────────────

@router.get("/ai/stock-alerts", tags=["AI"])
async def ai_stock_alerts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.stock_quantity <= Product.critical_limit))
    critical = result.scalars().all()

    if not critical:
        return {"durum": "normal", "kritik_urun_sayisi": 0, "uyarilar": [], "ai_analizi": None}

    try:
        from app.services.ai_service import ai_service
        ai_analizi = await ai_service.analyze_stock_alerts(critical)
    except Exception:
        ai_analizi = "AI analizi şu an kullanılamıyor."

    return {
        "durum": "kritik",
        "kritik_urun_sayisi": len(critical),
        "uyarilar": [
            {"id": p.id, "sku": p.sku, "urun": p.name, "stok": p.stock_quantity, "limit": p.critical_limit}
            for p in critical
        ],
        "ai_analizi": ai_analizi,
    }


@router.post("/supplier/draft", tags=["AI"])
async def supplier_draft(product_id: int, quantity: int = 50, db: AsyncSession = Depends(get_db)):
    if quantity <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Miktar 0'dan büyük olmalı.")
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Ürün bulunamadı: ID={product_id}")

    try:
        from app.services.ai_service import ai_service
        taslak = await ai_service.generate_stock_alert_email(
            product.name, product.stock_quantity, product.supplier_email or "belirtilmemiş"
        )
    except Exception:
        taslak = (
            f"Sayın Yetkili,\n\n'{product.name}' ürününde stok kritik seviyeye düştü "
            f"(mevcut: {product.stock_quantity} adet). {quantity} adet sipariş talebi iletiyoruz.\n\nSyntra"
        )

    return {"urun_id": product.id, "tedarikci_email": product.supplier_email, "miktar": quantity, "taslak": taslak}


# ── Notifications ─────────────────────────────

VALID_CHANNELS = {"system", "email", "whatsapp", "telegram"}


@router.post("/notifications/send", tags=["Notifications"])
async def send_notification(
    title: str,
    message: str,
    channel: Literal["system", "email", "whatsapp", "telegram"] = "system",
):
    from app.services.notification_service import dispatch
    await dispatch(channel=channel, title=title, message=message)
    return {"durum": "gonderildi", "kanal": channel, "baslik": title}


# ── Operations ───────────────────────────────

@router.get("/operations/summary", tags=["Operations"])
async def operations_summary(db: AsyncSession = Depends(get_db)):
    products = (await db.execute(select(Product))).scalars().all()
    critical = [p for p in products if p.stock_quantity <= p.critical_limit]
    pending = (await db.execute(select(Order).where(Order.status == "Bekliyor"))).scalars().all()

    return {
        "toplam_urun": len(products),
        "kritik_stok_sayisi": len(critical),
        "bekleyen_siparis": len(pending),
        "sistem_durumu": "kritik" if critical else "normal",
        "kritik_urunler": [
            {"id": p.id, "urun": p.name, "sku": p.sku, "stok": p.stock_quantity}
            for p in critical
        ],
    }
