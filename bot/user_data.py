import json
import os

USER_DATA_FILE = "user_data.json"

def load_data():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def set_subscription(user_id: int, level: int):
    data = load_data()
    str_id = str(user_id)
    if str_id not in data:
        data[str_id] = {}
    data[str_id]["subscription"] = level
    save_data(data)

def get_subscription(user_id: int):
    data = load_data()
    return data.get(str(user_id), {}).get("subscription", 0)
