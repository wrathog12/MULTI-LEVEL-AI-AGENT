import os
import logging
from google import genai

class GemmaClient:
    def __init__(self):
        api_key = os.getenv("Gemini_API_TOKEN")
        if not api_key:
            raise ValueError("Gemini_API_KEY not set in environment")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemma-3-27b-it"

    def generate_text(self, prompt: str, max_tokens: int = 300) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logging.error(f"Gemma API call failed: {e}")
            return "Sorry, the AI service is temporarily unavailable. Please try again later."

    def summarize(self, prompt: str, max_tokens: int = 300) -> str:
        # For now, summarization uses the same generation method
        return self.generate_text(prompt, max_tokens)
