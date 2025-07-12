import asyncio
import logging
import signal
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.config import config
from bot.bot_instance import bot
from bot.services.scheduler import news_scheduler
from bot.utils.together_api import together_api

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

class NewsBot:
    def __init__(self):
        self.is_running = False
        self.tasks = []
    
    async def start(self):
        """Запускает бота"""
        try:
            logger.info("🚀 Запуск новостного бота...")
            
            # Проверяем конфигурацию
            logger.info("⚙️ Проверка конфигурации...")
            if not config.validate():
                logger.error("❌ Некорректная конфигурация")
                return False
            
            config.log_config()
            
            # Тестируем AI API
            logger.info("🧠 Тестирование AI API...")
            if not await together_api.test_connection():
                logger.error("❌ Ошибка подключения к AI API")
                return False
            
            logger.info("✅ AI API работает корректно")
            
            # Запускаем планировщик
            logger.info("📅 Запуск планировщика новостей...")
            scheduler_task = asyncio.create_task(news_scheduler.start())
            self.tasks.append(scheduler_task)
            
            # Запускаем бота
            logger.info("🤖 Запуск Telegram бота...")
            bot_task = asyncio.create_task(bot.infinity_polling(none_stop=True))
            self.tasks.append(bot_task)
            
            self.is_running = True
            logger.info("✅ Бот успешно запущен!")
            
            # Ждем завершения всех задач
            await asyncio.gather(*self.tasks)
            
        except KeyboardInterrupt:
            logger.info("⏹️ Получен сигнал остановки")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            return False
        finally:
            await self.stop()
        
        return True
    
    async def stop(self):
        """Останавливает бота"""
        if not self.is_running:
            return
        
        logger.info("🛑 Остановка бота...")
        self.is_running = False
        
        # Останавливаем планировщик
        await news_scheduler.stop()
        
        # Отменяем все задачи
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Ждем завершения отмены
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        logger.info("✅ Бот остановлен")

async def main():
    """Главная функция"""
    news_bot = NewsBot()
    
    # Обработчик сигналов для корректного завершения
    def signal_handler(signum, frame):
        logger.info(f"🔔 Получен сигнал {signum}")
        asyncio.create_task(news_bot.stop())
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Запускаем бота
        success = await news_bot.start()
        if not success:
            logger.error("❌ Не удалось запустить бота")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Программа прервана пользователем")
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)
