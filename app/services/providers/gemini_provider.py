from google import genai
from google.genai import types

from app.config import settings
from app.services.providers.base_provider import BaseAIProvider


class GeminiProvider(BaseAIProvider):

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model_id = "gemini-2.5-flash"

    async def generate_content(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:

        response = await self.client.aio.models.generate_content(

            model=self.model_id,

            contents=user_prompt,

            config=types.GenerateContentConfig(

                system_instruction=system_prompt,

                temperature=0.4,

                max_output_tokens=300
            )
        )

        return response.text