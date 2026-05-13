from abc import ABC, abstractmethod


class BaseAIProvider(ABC):

    @abstractmethod
    async def generate_content(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:
        pass

#İlerde Gemini yerine GPT kullanırsak, hiçbir endpoint değişmez.