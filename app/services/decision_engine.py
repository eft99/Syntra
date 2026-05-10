from app.services.event_bus import bus
from app.models import Product


async def evaluate_stock(product: Product):
    if product.stock_quantity <= product.critical_limit:
        await bus.publish("stock_below_threshold", {
            "product_id": product.id,
            "sku": product.sku,
            "name": product.name,
            "stock": product.stock_quantity,
            "limit": product.critical_limit,
        })


async def evaluate_order(order_id: int, customer_name: str):
    await bus.publish("order_created", {
        "order_id": order_id,
        "customer_name": customer_name,
    })
