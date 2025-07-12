import os
import logging
from pathlib import Path
from typing import Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def load_env_file(env_file: str = '.env.local') -> None:
    """Загружает переменные окружения из файла"""
    env_path = Path(env_file)
    if not env_path.exists():
        logger.warning(f"Файл {env_file} не найден")
        return
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
        logger.info(f"✅ Переменные окружения загружены из {env_file}")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки {env_file}: {e}")

# Загружаем переменные окружения
load_env_file('.env.local')

class Config:
    """Конфигурация бота"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv('BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN', '')
    ADMIN_ID: int = int(os.getenv('ADMIN_ID', '0'))
    
    # AI API Keys
    TOGETHER_API_KEY: str = os.getenv('TOGETHER_API_KEY', '')
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql://newsbot:newsbot123@postgres:5432/newsbot_db')
    POSTGRES_DB: str = os.getenv('POSTGRES_DB', 'newsbot_db')
    POSTGRES_USER: str = os.getenv('POSTGRES_USER', 'newsbot')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', 'newsbot123')
    
    # Redis
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    
    # News Archive
    NEWS_ARCHIVE_PATH: str = os.getenv('NEWS_ARCHIVE_PATH', '/app/news_archive')
    MAX_NEWS_PER_CATEGORY: int = int(os.getenv('MAX_NEWS_PER_CATEGORY', '50'))
    NEWS_CACHE_HOURS: int = int(os.getenv('NEWS_CACHE_HOURS', '48'))
    
    # Bot Settings
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    WEBHOOK_URL: str = os.getenv('WEBHOOK_URL', '')
    WEBHOOK_PORT: int = int(os.getenv('WEBHOOK_PORT', '8080'))
    
    # Scheduler Settings
    UPDATE_INTERVAL_MINUTES: int = int(os.getenv('UPDATE_INTERVAL_MINUTES', '10'))
    CLEANUP_INTERVAL_HOURS: int = int(os.getenv('CLEANUP_INTERVAL_HOURS', '6'))
    REPORT_INTERVAL_HOURS: int = int(os.getenv('REPORT_INTERVAL_HOURS', '24'))
    
    # AI Processing Settings
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    AI_TIMEOUT_SECONDS: int = int(os.getenv('AI_TIMEOUT_SECONDS', '30'))
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '5'))
    
    # Telegram Message Limits
    MAX_MESSAGE_LENGTH: int = 4096
    MAX_CAPTION_LENGTH: int = 1024
    
    # News Processing Settings - убрано ограничение на минимальный возраст
    MAX_NEWS_AGE_HOURS: int = 48
    
    @classmethod
    def validate(cls) -> bool:
        """Проверяет корректность конфигурации"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN не установлен")
        
        if not cls.ADMIN_ID:
            errors.append("ADMIN_ID не установлен")
        
        if not cls.TOGETHER_API_KEY:
            errors.append("TOGETHER_API_KEY не установлен")
        
        if errors:
            for error in errors:
                logger.error(f"❌ {error}")
            return False
        
        logger.info("✅ Конфигурация корректна")
        return True
    
    @classmethod
    def log_config(cls) -> None:
        """Логирует основные параметры конфигурации"""
        logger.info(f"🤖 Bot Token: {cls.BOT_TOKEN[:10]}...")
        logger.info(f"🧠 Together API: {cls.TOGETHER_API_KEY[:10]}...")
        logger.info(f"👑 Admin ID: {cls.ADMIN_ID}")
        logger.info(f"📁 Archive Path: {cls.NEWS_ARCHIVE_PATH}")
        logger.info(f"🔄 Update Interval: {cls.UPDATE_INTERVAL_MINUTES} min")
        logger.info(f"📰 Max News Age: {cls.MAX_NEWS_AGE_HOURS} hours")

# Создаем экземпляр конфигурации
config = Config()

# Проверяем конфигурацию при импорте
if not config.validate():
    raise ValueError("Некорректная конфигурация бота")
