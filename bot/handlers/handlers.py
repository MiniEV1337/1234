"""
Основные обработчики команд и сообщений бота
"""
import logging
import asyncio
from typing import List, Dict, Any
from aiogram import types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.bot_instance import dp, bot
from bot.data.rss_feeds import RSS_FEEDS
from bot.utils.rss_parser import parse_rss_feed
from bot.utils.html_utils import format_news_html

logger = logging.getLogger(__name__)

# Клавиатура с категориями новостей
def get_categories_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с категориями новостей"""
    buttons = []
    
    # Группируем кнопки по 2 в ряд
    categories = list(RSS_FEEDS.keys())
    for i in range(0, len(categories), 2):
        row = []
        for j in range(i, min(i + 2, len(categories))):
            category = categories[j]
            # Переводим названия категорий на русский
            category_names = {
                'ai': '🤖 ИИ',
                'technology': '💻 Технологии',
                'gaming': '🎮 Игры',
                'crypto': '₿ Крипто',
                'science': '🔬 Наука',
                'politics': '🏛️ Политика',
                'economy': '💰 Экономика',
                'culture': '🎭 Культура',
                'world': '🌍 Мир',
                'cinema': '🎬 Кино',
                'medicine': '⚕️ Медицина'
            }
            
            button_text = category_names.get(category, category.title())
            row.append(InlineKeyboardButton(
                text=button_text,
                callback_data=f"category_{category}"
            ))
        buttons.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    try:
        welcome_text = (
            "🗞️ <b>Добро пожаловать в Новостной Бот!</b>\n\n"
            "Я помогу вам получать актуальные новости по различным категориям.\n"
            "Выберите интересующую вас категорию:"
        )
        
        keyboard = get_categories_keyboard()
        
        await message.answer(
            welcome_text,
            reply_markup=keyboard
        )
        
        logger.info(f"Пользователь {message.from_user.id} запустил бота")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    try:
        help_text = (
            "📖 <b>Помощь по использованию бота</b>\n\n"
            "🔹 /start - Главное меню с категориями\n"
            "🔹 /help - Эта справка\n"
            "🔹 /categories - Показать все категории\n\n"
            "Просто выберите категорию новостей, и я пришлю вам последние новости!"
        )
        
        await message.answer(help_text)
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /help: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@dp.message(Command("categories"))
async def cmd_categories(message: types.Message):
    """Обработчик команды /categories"""
    try:
        keyboard = get_categories_keyboard()
        
        await message.answer(
            "📂 <b>Выберите категорию новостей:</b>",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /categories: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")

@dp.callback_query(lambda c: c.data and c.data.startswith('category_'))
async def process_category_callback(callback_query: types.CallbackQuery):
    """Обработчик выбора категории новостей"""
    try:
        await callback_query.answer()
        
        category = callback_query.data.replace('category_', '')
        
        # Отправляем сообщение о загрузке
        loading_msg = await callback_query.message.answer(
            f"⏳ Загружаю новости по категории <b>{category}</b>..."
        )
        
        # Получаем новости
        news_items = await get_news_by_category(category)
        
        if not news_items:
            await loading_msg.edit_text(
                f"😔 К сожалению, новости по категории <b>{category}</b> сейчас недоступны.\n"
                "Попробуйте позже или выберите другую категорию."
            )
            return
        
        # Удаляем сообщение о загрузке
        await loading_msg.delete()
        
        # Отправляем новости (максимум 5)
        max_news = min(5, len(news_items))
        
        for i, news_item in enumerate(news_items[:max_news]):
            try:
                formatted_news = format_news_html(news_item)
                await callback_query.message.answer(formatted_news)
                
                # Небольшая задержка между сообщениями
                if i < max_news - 1:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"Ошибка отправки новости {i}: {e}")
                continue
        
        # Добавляем кнопку "Еще новости"
        more_button = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="🔄 Еще новости",
                callback_data=f"category_{category}"
            ),
            InlineKeyboardButton(
                text="📂 Все категории",
                callback_data="show_categories"
            )
        ]])
        
        await callback_query.message.answer(
            f"📰 Показано {max_news} новостей по категории <b>{category}</b>",
            reply_markup=more_button
        )
        
        logger.info(f"Отправлено {max_news} новостей категории {category} пользователю {callback_query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике категории {category}: {e}")
        await callback_query.message.answer("❌ Произошла ошибка при загрузке новостей. Попробуйте позже.")

@dp.callback_query(lambda c: c.data == 'show_categories')
async def show_categories_callback(callback_query: types.CallbackQuery):
    """Показать все категории"""
    try:
        await callback_query.answer()
        
        keyboard = get_categories_keyboard()
        
        await callback_query.message.answer(
            "📂 <b>Выберите категорию новостей:</b>",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Ошибка показа категорий: {e}")

async def get_news_by_category(category: str) -> List[Dict[str, Any]]:
    """Получает новости по категории"""
    try:
        if category not in RSS_FEEDS:
            logger.warning(f"Неизвестная категория: {category}")
            return []
        
        feeds = RSS_FEEDS[category]
        all_news = []
        
        for feed_url in feeds:
            try:
                logger.info(f"Парсим RSS: {feed_url}")
                news_items = await parse_rss_feed(feed_url)
                all_news.extend(news_items)
                
            except Exception as e:
                logger.error(f"Ошибка парсинга RSS {feed_url}: {e}")
                continue
        
        # Сортируем по дате (новые сначала)
        all_news.sort(key=lambda x: x.get('published_parsed', (0,)), reverse=True)
        
        logger.info(f"Получено {len(all_news)} новостей для категории {category}")
        return all_news
        
    except Exception as e:
        logger.error(f"Ошибка получения новостей для категории {category}: {e}")
        return []

# Обработчик неизвестных сообщений
@dp.message()
async def handle_unknown_message(message: types.Message):
    """Обработчик неизвестных сообщений"""
    try:
        keyboard = get_categories_keyboard()
        
        await message.answer(
            "🤔 Я не понимаю эту команду.\n"
            "Выберите категорию новостей:",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике неизвестных сообщений: {e}")
