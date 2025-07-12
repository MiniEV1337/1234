from together import Together
import os

class NewsSummarizer:
    def __init__(self):
        self.api_key = os.getenv("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("❌ TOGETHER_API_KEY не найден в окружении")

        self.client = Together(api_key=self.api_key)
        self.model = "meta-llama/Llama-3-8b-chat-hf"  # можно заменить на другой

    async def summarize(self, text: str) -> str:
        if not text.strip():
            return "⚠️ Нет текста для краткого изложения"

        prompt = f"""
Ты — Telegram-бот, который помогает пользователям быстро понять суть новостной статьи.

Вот новость:
{text}

Сделай краткое и понятное резюме в 4–5 предложениях.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()
