from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from bot.keyboards.keyboards import get_main_menu
from bot.data.rss_feeds import RSS_FEEDS
from bot.utils.rss_parser import get_first_news
from bot.utils.html_utils import clean_html

router = Router()


@router.message(Command("news"))
async def show_news_categories(message: Message):
    await message.answer(
        "🗂 Выберите категорию новостей:",
        reply_markup=get_main_menu()
    )


@router.callback_query(F.data.in_(list(RSS_FEEDS.keys())))
async def send_news_by_category(callback: CallbackQuery):
    category = callback.data
    url = RSS_FEEDS.get(category)

    if not url:
        await callback.answer("❌ Неизвестная категория", show_alert=True)
        return

    news = get_first_news(url)

    if news:
        title, summary, link = news

        text = (
            f"<b>{title}</b>\n\n"
            f"{clean_html(summary)}\n\n"
            f"<a href='{link}'>🔗 Подробнее</a>"
        )

        await callback.message.answer(text, parse_mode="HTML", disable_web_page_preview=False)
    else:
        await callback.message.answer("🚫 Не удалось получить новости по этой категории.")


def register_rss(dp):
    dp.include_router(router)
