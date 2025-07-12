import json
import os

NEWS_HISTORY_FILE = "news_history.json"

def load_history():
    if not os.path.exists(NEWS_HISTORY_FILE):
        return {}
    with open(NEWS_HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_history(data):
    with open(NEWS_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_viewed_news(user_id: int, category: str, news_id: str):
    data = load_history()
    str_id = str(user_id)
    if str_id not in data:
        data[str_id] = {}
    if category not in data[str_id]:
        data[str_id][category] = []
    if news_id not in data[str_id][category]:
        data[str_id][category].append(news_id)
    save_history(data)

def has_viewed(user_id: int, category: str, news_id: str) -> bool:
    data = load_history()
    return news_id in data.get(str(user_id), {}).get(category, [])
