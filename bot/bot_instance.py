import logging
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from bot.config import config
from bot.handlers.start.start import register_start_handlers
from bot.handlers.simple_handlers import register_simple_handlers

logger = logging.getLogger(__name__)

# Создаем экземпляр бота
bot = AsyncTeleBot(config.BOT_TOKEN)

# Регистрируем обработчики
register_start_handlers(bot)
register_simple_handlers(bot)

logger.info("🤖 Telegram бот инициализирован")
