from google import genai
from google.genai import types
from app.config import settings


class AIService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = "gemini-2.5-flash"

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
            f"- {p.name} (SKU: {p.sku}): Mevcut Stok={p.stock_quantity}, Kritik Limit={p.critical_limit}"
            for p in products
        )
        prompt = (
            f"Aşağıdaki ürünler kritik stok seviyesinin altına düşmüştür:\n{product_list}\n\n"
            "Sen Syntra Akıllı Operasyon Asistanısın. Bu verileri analiz ederek operasyon müdürüne şu yapıda bir rapor sun:\n"
            "1. **Kritiklik Analizi:** Hangi ürünlerin tükenme riski daha yüksek? (Aciliyet Skoru: 1-10)\n"
            "2. **Akıllı Sipariş Önerisi:** Mevcut limitleri ve stok durumunu göz önüne alarak, her ürün için 'Önerilen Sipariş Miktarı' tahmini yap.\n"
            "3. **Operasyonel Tavsiye:** Tedarik zinciri aksamaması için atılması gereken ilk 3 adımı belirt.\n\n"
            "Yanıtın profesyonel, veriye dayalı ve kısa-öz olsun."
        )
        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            contents=prompt,
        )
        return response.text


ai_service = AIService()
