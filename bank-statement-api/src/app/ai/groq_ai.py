import os
from typing import Optional

from groq import Groq


class GroqAI:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "llama-3.3-70b-versatile",
    ):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either as an argument or as GROQ_API_KEY environment variable"
            )

        self.model_name = model_name

        # Initialize the Groq client
        self.client = Groq(
            api_key=self.api_key,
        )

    async def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
