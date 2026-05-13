from urllib import response

from app.services.providers.gemini_provider import GeminiProvider

from app.services.prompts.stock_alert_prompt import (
    SYSTEM_PROMPT,
    build_stock_email_prompt,
    build_stock_analysis_prompt
)

from app.services.utils.cleanup import clean_ai_response


class AIService:

    def __init__(self):

        self.provider = GeminiProvider()

    async def generate_stock_alert_email(
        self,
        product_name: str,
        current_stock: int,
        critical_limit: int,
        supplier_email: str
    ):

        try:

            prompt = build_stock_email_prompt(
                product_name,
                current_stock,
                critical_limit,
                supplier_email
            )

            response = await self.provider.generate_content(
                SYSTEM_PROMPT,
                prompt
            )

            return {
                "success": True,
                "content": clean_ai_response(response)
            }

        except Exception as e:

            return {
                "success": False,
                "content": (
                    "Critical stock detected. "
                    "Immediate supplier communication recommended."
                ),
                "error": str(e)
            }

    async def analyze_stock_alerts(self, products: list):

        try:

            prompt = build_stock_analysis_prompt(products)

            response = await self.provider.generate_content(
                SYSTEM_PROMPT,
                prompt
            )
            cleaned_response = clean_ai_response(response)
            return {
                "success": True,
                "content": clean_ai_response(response)
            }

        except Exception as e:

            return {
                "success": False,
                "content": (
                    "Multiple products are below critical stock threshold. "
                    "Operational risk level increased."
                ),
                "error": str(e)
            }


ai_service = AIService()