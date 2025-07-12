import logging
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from bot.config import config
from bot.utils.news_cache import news_cache
from bot.services.scheduler import news_scheduler

logger = logging.getLogger(__name__)

def register_simple_handlers(bot: AsyncTeleBot):
    """Регистрирует простые обработчики команд"""
    
    @bot.message_handler(commands=['news'])
    async def handle_news_command(message):
        """Обработчик команды /news"""
        try:
            user_id = message.from_user.id
            logger.info(f"👤 Пользователь {user_id} запросил новости")
            
            # Получаем последние новости
            latest_news = await news_cache.get_latest_news(limit=5)
            
            if not latest_news:
                await bot.reply_to(message, "📰 Новости пока не загружены. Попробуйте позже.")
                return
            
            # Формируем ответ
            response = "📰 **Последние новости:**\n\n"
            
            for i, news_item in enumerate(latest_news, 1):
                title = news_item.get('title', 'Без заголовка')
                summary = news_item.get('summary', '')
                link = news_item.get('link', '')
                source = news_item.get('source_title', 'Неизвестный источник')
                
                # Ограничиваем длину
                if len(summary) > 200:
                    summary = summary[:197] + '...'
                
                response += f"**{i}. {title}**\n"
                if summary:
                    response += f"{summary}\n"
                response += f"🔗 [Читать полностью]({link})\n"
                response += f"📡 {source}\n\n"
            
            await bot.reply_to(message, response, parse_mode='Markdown', disable_web_page_preview=True)
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки команды /news: {e}")
            await bot.reply_to(message, "❌ Произошла ошибка при получении новостей.")
    
    @bot.message_handler(commands=['status'])
    async def handle_status_command(message):
        """Обработчик команды /status (только для админа)"""
        try:
            user_id = message.from_user.id
            
            if user_id != config.ADMIN_ID:
                await bot.reply_to(message, "❌ У вас нет прав для выполнения этой команды.")
                return
            
            logger.info(f"👑 Админ {user_id} запросил статус системы")
            
            # Получаем статистику
            cache_stats = await news_cache.get_cache_stats()
            scheduler_status = await news_scheduler.get_scheduler_status()
            
            response = "📊 **Статус системы:**\n\n"
            response += f"🤖 **Планировщик:** {'✅ Работает' if scheduler_status.get('is_running') else '❌ Остановлен'}\n"
            response += f"📰 **Всего новостей:** {cache_stats.get('total_news', 0)}\n"
            response += f"📂 **Категорий:** {len(cache_stats.get('categories', {}))}\n"
            response += f"💾 **Размер кеша:** {cache_stats.get('cache_size_mb', 0)} МБ\n"
            response += f"🔄 **Активных задач:** {scheduler_status.get('active_tasks', 0)}\n\n"
            
            # Детали по категориям
            categories = cache_stats.get('categories', {})
            if categories:
                response += "📋 **По категориям:**\n"
                for category, info in categories.items():
                    count = info.get('count', 0)
                    response += f"• {category}: {count} новостей\n"
            
            await bot.reply_to(message, response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки команды /status: {e}")
            await bot.reply_to(message, "❌ Произошла ошибка при получении статуса.")
    
    @bot.message_handler(commands=['update'])
    async def handle_update_command(message):
        """Обработчик команды /update (только для админа)"""
        try:
            user_id = message.from_user.id
            
            if user_id != config.ADMIN_ID:
                await bot.reply_to(message, "❌ У вас нет прав для выполнения этой команды.")
                return
            
            logger.info(f"👑 Админ {user_id} запросил принудительное обновление")
            
            await bot.reply_to(message, "🔄 Запускаю принудительное обновление новостей...")
            
            # Запускаем принудительное обновление
            results = await news_scheduler.force_full_update()
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            response = f"✅ Обновление завершено: {successful}/{total} категорий обновлено\n\n"
            
            for category, success in results.items():
                status = "✅" if success else "❌"
                response += f"{status} {category}\n"
            
            await bot.reply_to(message, response)
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки команды /update: {e}")
            await bot.reply_to(message, "❌ Произошла ошибка при обновлении.")
    
    @bot.message_handler(commands=['help'])
    async def handle_help_command(message):
        """Обработчик команды /help"""
        try:
            user_id = message.from_user.id
            
            response = """
🤖 **Доступные команды:**

📰 /news - Получить последние новости
❓ /help - Показать это сообщение
ℹ️ /start - Начать работу с ботом
"""
            
            # Добавляем админские команды для админа
            if user_id == config.ADMIN_ID:
                response += """
👑 **Команды администратора:**

📊 /status - Статус системы
🔄 /update - Принудительное обновление
"""
            
            await bot.reply_to(message, response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки команды /help: {e}")
            await bot.reply_to(message, "❌ Произошла ошибка.")
    
    logger.info("✅ Простые обработчики зарегистрированы")
