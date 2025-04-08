import os
from typing import Dict, List, Optional

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory


class GeminiPro:
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
            generation_config={
                "temperature": self.temperature,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )

    async def generate(self, prompt: str) -> str:
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        try:
            chat = self.model.start_chat()

            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")

                if role == "user":
                    response = await chat.send_message_async(content)
                    return response.text
        except Exception as e:
            raise Exception(f"Error in chat: {str(e)}")
        try:
            chat = self.model.start_chat()

            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")

                if role == "user":
                    response = await chat.send_message_async(content)

            return response.text
        except Exception as e:
            raise Exception(f"Error in chat: {str(e)}")
