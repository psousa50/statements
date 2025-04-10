import os
from typing import Dict, List, Optional

import google.generativeai as genai

from src.app.ai.llm_client import LLMClient


class GeminiAI(LLMClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-pro-exp-03-25",
        temperature: float = 0,
    ):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either as an argument or as GOOGLE_API_KEY environment variable"
            )

        self.model_name = model_name

        genai.configure(api_key=self.api_key)

        self.model = genai.GenerativeModel(
            model_name=self.model_name,
        )

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

    async def generate_async(self, prompt: str) -> str:
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
