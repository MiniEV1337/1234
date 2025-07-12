from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from itertools import zip_longest

def chunked(data, size):
    args = [iter(data)] * size
    return list(filter(None, map(lambda x: list(filter(None, x)), zip_longest(*args))))

def get_main_menu():
    buttons_data = [
        ("📰 Политика", "politics"),
        ("💻 Технологии", "technology"),
        ("🏀 Спорт", "sports"),
        ("📊 Экономика", "economy"),
        ("🎭 Культура", "culture"),
        ("🌍 Мир", "world"),
        ("🔬 Наука", "science"),
        ("🎮 Игры", "gaming"),
        ("📽 Кино", "cinema"),
        ("💊 Медицина", "medicine")
    ]
    
    buttons = [InlineKeyboardButton(text=text, callback_data=data) for text, data in buttons_data]
    keyboard = InlineKeyboardMarkup(inline_keyboard=chunked(buttons, 3))  # 3 в ряд

    return keyboard

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton(text=title, callback_data=code)] for title, code in NEWS_CATEGORIES
    ]
    keyboard.append(
        [InlineKeyboardButton(text="🔧 Настройки", callback_data="open_settings")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_settings_menu(is_admin=False):
    buttons = [
        [InlineKeyboardButton(text="💎 Подписка", callback_data="subscription")],
        [InlineKeyboardButton(text="🌙 Новости ночью", callback_data="toggle_night")],
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data="my_stats")],
        [InlineKeyboardButton(text="📌 Любимые темы", callback_data="select_favorites")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_subscription_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Подписка 1 уровня", callback_data="subscribe_1")],
        [InlineKeyboardButton(text="🌟 Подписка 2 уровня", callback_data="subscribe_2")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_settings")]
    ])

def get_category_selector(selected: list[str], limit: int):
    buttons = []
    for title, code in NEWS_CATEGORIES:
        mark = "✅ " if code in selected else ""
        buttons.append([InlineKeyboardButton(
            text=f"{mark}{title}",
            callback_data=f"toggle_cat:{code}"
        )])
    buttons.append([InlineKeyboardButton(text="💾 Сохранить выбор", callback_data="save_categories")])
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_settings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
