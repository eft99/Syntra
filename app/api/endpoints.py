from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Product

from app.services.ai_service import ai_service
from app.services.adapter import get_erp_adapter

router = APIRouter()


@router.get("/ai/stock-alerts")
async def get_ai_stock_alerts(
    db: AsyncSession = Depends(get_db)
):

    stmt = select(Product).where(
        Product.stock_quantity < Product.critical_limit
    )

    result = await db.execute(stmt)

    low_stock_products = result.scalars().all()

    if not low_stock_products:

        return {
            "status": "success",
            "analysis": "All stock levels are safe.",
            "alerts": []
        }

    analysis_result = await ai_service.analyze_stock_alerts(
        low_stock_products
    )

    alerts = []

    for prod in low_stock_products:

        email_result = await ai_service.generate_stock_alert_email(
            product_name=prod.name,
            current_stock=prod.stock_quantity,
            critical_limit=prod.critical_limit,
            supplier_email=prod.supplier_email or "unknown"
        )

        alerts.append({
            "product": prod.name,
            "sku": prod.sku,
            "current_stock": prod.stock_quantity,
            "critical_limit": prod.critical_limit,
            "supplier_email": prod.supplier_email,
            "ai_email": email_result["content"]
        })

    return {
        "status": "success",
        "analysis": analysis_result["content"],
        "alerts": alerts
    }

@router.get("/erp/status")
async def get_erp_status():

    adapter = get_erp_adapter()

    orders = await adapter.get_remote_orders()

    stock_data = await adapter.get_stock_data()

    return {
        "erp_mode": adapter.__class__.__name__,
        "orders": orders,
        "stock_data": stock_data
    }