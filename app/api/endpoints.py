import io
import logging
import uuid
from typing import List, Literal, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Order, OrderItem, Product
from app.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    NotificationRequest,
    OrderCreate,
    OrderRead,
    ProductCreate,
    ProductRead,
    SupplierDraftRequest,
    UserCreate,
    UserRead,
    Token,
)
from app.services.auth_service import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
)
from app.models import User
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address

security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)


logger = logging.getLogger(__name__)

router = APIRouter()

_REGISTERED_RESET_EMAILS = frozenset(
    {
        "admin@syntra.app",
        "musteri@syntra.app",
    }
)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz veya süresi dolmuş token")
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token kullanıcı bilgisi içermiyor")
        
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı")
    return user

def require_role(role: str):
    async def role_checker(user: User = Depends(get_current_user)):
        if user.role != role and user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu işlem için yetkiniz yok")
        return user
    return role_checker


ALLOWED_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/products", response_model=List[ProductRead], tags=["Ürünler"])
async def list_products(
    skip: int = 0, 
    limit: int = 20, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if skip < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="'skip' değeri negatif olamaz.")
    limit = min(max(limit, 1), 100)
    result = await db.execute(select(Product).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/products/{product_id}", response_model=ProductRead, tags=["Ürünler"])
async def get_product(
    product_id: int, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if product_id <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Geçersiz ürün ID'si.")
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Ürün bulunamadı: ID={product_id}")
    return product


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED, tags=["Ürünler"])
async def create_product(
    data: ProductCreate, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin"))
):
    existing = await db.execute(select(Product).where(Product.sku == data.sku))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, detail=f"Bu ürün kodu zaten kayıtlı: {data.sku}")
    product = Product(**data.model_dump())
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product


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
async def upload_products(
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin"))
):
    if not file.filename or not file.filename.endswith(".xlsx") or file.content_type != ALLOWED_MIME:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Sadece .xlsx dosyaları kabul edilir.")

    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Dosya boyutu 5MB'ı geçemez.")

    try:
        df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
    except Exception:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Excel dosyası okunamadı.")

    if not {"sku", "name", "stock_quantity"}.issubset(df.columns):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Zorunlu sütunlar eksik: sku, name, stock_quantity")

    df = df.where(pd.notna(df), None)
    added, updated, errors = 0, 0, []

    for idx, row in df.iterrows():
        try:
            sku = str(row["sku"]).strip().upper()
            if not sku:
                raise ValueError("Ürün kodu boş olamaz.")
            result = await db.execute(select(Product).where(Product.sku == sku))
            existing = result.scalar_one_or_none()
            if existing:
                existing.name = str(row["name"]).strip()
                existing.stock_quantity = int(row["stock_quantity"])
                existing.critical_limit = int(row.get("critical_limit") or 10)
                existing.supplier_email = row.get("supplier_email")
                updated += 1
            else:
                db.add(Product(
                    sku=sku,
                    name=str(row["name"]).strip(),
                    stock_quantity=int(row["stock_quantity"]),
                    critical_limit=int(row.get("critical_limit") or 10),
                    supplier_email=row.get("supplier_email"),
                ))
                added += 1
        except Exception:
            errors.append({"satir": int(idx) + 2, "hata": "Bu satır işlenemedi, veriyi kontrol edin."})

    return {"eklenen": added, "guncellenen": updated, "hatalar": errors}


@router.get("/orders", response_model=List[OrderRead], tags=["Siparişler"])
async def list_orders(
    status_filter: Optional[str] = None, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = select(Order).options(selectinload(Order.items))
    if status_filter:
        gecerli_durumlar = {"Bekliyor", "Tamamlandı", "İptal"}
        if status_filter not in gecerli_durumlar:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Geçersiz durum filtresi. Seçenekler: {', '.join(gecerli_durumlar)}")
        query = query.where(Order.status == status_filter)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED, tags=["Siparişler"])
async def create_order(
    data: OrderCreate, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
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


@router.get("/ai/stock-alerts", tags=["Yapay Zeka"])
@limiter.limit("10/minute")
async def ai_stock_alerts(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = await db.execute(select(Product).where(Product.stock_quantity <= Product.critical_limit))
    critical = result.scalars().all()

    if not critical:
        return {"durum": "normal", "kritik_urun_sayisi": 0, "uyarilar": [], "ai_analizi": None}

    try:
        from app.services.ai_service import ai_service
        ai_analizi = await ai_service.analyze_stock_alerts(critical)
    except Exception as e:
        logger.error("Yapay zeka stok analizi başarısız oldu: %s", e)
        ai_analizi = "Yapay zeka analizi şu an kullanılamıyor."

    return {
        "durum": "kritik",
        "kritik_urun_sayisi": len(critical),
        "uyarilar": [
            {"id": p.id, "sku": p.sku, "urun": p.name, "stok": p.stock_quantity, "limit": p.critical_limit}
            for p in critical
        ],
        "ai_analizi": ai_analizi,
    }


@router.post("/supplier/draft", tags=["Yapay Zeka"])
async def supplier_draft(
    data: SupplierDraftRequest, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = await db.execute(select(Product).where(Product.id == data.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Ürün bulunamadı: ID={data.product_id}")

    try:
        from app.services.ai_service import ai_service
        taslak = await ai_service.generate_stock_alert_email(
            product.name, product.stock_quantity, product.supplier_email or "belirtilmemiş"
        )
    except Exception as e:
        logger.error("Tedarikçi e-postası oluşturulamadı: %s", e)
        taslak = (
            f"Sayın Yetkili,\n\n'{product.name}' ürününde stok kritik seviyeye düştü "
            f"(mevcut: {product.stock_quantity} adet). {data.quantity} adet sipariş talebi iletiyoruz.\n\nSyntra"
        )

    return {"urun_id": product.id, "tedarikci_email": product.supplier_email, "miktar": data.quantity, "taslak": taslak}


@router.post("/notifications/send", tags=["Bildirimler"])
async def send_notification(
    data: NotificationRequest,
    user: User = Depends(require_role("admin"))
):
    from app.services.notification_service import dispatch
    await dispatch(channel=data.channel, title=data.title, message=data.message)
    return {"durum": "gönderildi", "kanal": data.channel, "baslik": data.title}


@router.post(
    "/auth/forgot-password",
    response_model=ForgotPasswordResponse,
    tags=["Auth"],
)
async def forgot_password(body: ForgotPasswordRequest) -> ForgotPasswordResponse:
    """Kayıtlı e-posta için sıfırlama (demo; gerçek mail gönderilmez)."""
    sent = body.email in _REGISTERED_RESET_EMAILS
    return ForgotPasswordResponse(sent=sent)


@router.get("/operations/summary", tags=["Operasyon"])
async def operations_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
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


@router.post("/auth/register", response_model=UserRead, tags=["Auth"])
@limiter.limit("5/minute")
async def register(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(data.password)
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed_password,
        role="user"  # Default role
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/auth/login", response_model=Token, tags=["Auth"])
@limiter.limit("10/minute")
async def login(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Simple login using UserCreate schema for convenience (only username and password needed)
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

