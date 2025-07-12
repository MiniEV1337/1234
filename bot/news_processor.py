import os
import asyncio
from ai_engine.summarizer import NewsSummarizer
from bot.html_formatter import render_news

def handle_news(news_text: str) -> str:
    try:
        summarizer = NewsSummarizer()
        summary = asyncio.run(summarizer.summarize(news_text))
        return render_news("Срочная новость", summary)
    except Exception as e:
        print(f"[ERROR] Failed to summarize news: {e}")
        return "⚠️ Не удалось обработать новость."
