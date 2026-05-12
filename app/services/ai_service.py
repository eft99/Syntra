from google import genai
from google.genai import types
from app.config import settings


class AIService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = "gemini-2.0-flash"

    async def generate_stock_alert_email(self, product_name: str, current_stock: int, supplier_email: str) -> str:
        system_prompt = (
            "Sen bir KOBİ satın alma müdürüsün. Tedarikçilere karşı kibar ama "
            "işlerin aksamaması için aciliyet bildiren profesyonel e-postalar yazarsın."
        )
        user_prompt = (
            f"Ürün Adı: {product_name}\n"
            f"Mevcut Stok: {current_stock}\n"
            f"Tedarikçi: {supplier_email}\n\n"
            "Bu ürün kritik seviyenin altına düştü. Tedarikçiden yeni stok talep eden, "
            "fiyat teklifi isteyen kısa ve öz bir mail taslağı hazırlar mısın?"
        )
        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            ),
        )
        return response.text

    async def analyze_stock_alerts(self, products: list) -> str:
        product_list = "\n".join(
            f"- {p.name} (SKU: {p.sku}): stok={p.stock_quantity}, limit={p.critical_limit}"
            for p in products
        )
        prompt = (
            f"Aşağıdaki ürünlerin stoğu kritik seviyenin altına düşmüştür:\n{product_list}\n\n"
            "Operasyon müdürüne kısa, net ve aksiyona dönük bir analiz yaz. "
            "Öncelik sırasına göre aksiyon öner."
        )
        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            contents=prompt,
        )
        return response.text


ai_service = AIService()
