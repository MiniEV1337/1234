"""
Валидатор конфигурации для Telegram News Bot
"""
import os
import sys
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_config():
    """Проверяет конфигурацию бота"""
    errors = []
    warnings = []
    
    # Обязательные переменные
    required_vars = {
        'BOT_TOKEN': 'Токен Telegram бота',
    }
    
    # Опциональные переменные
    optional_vars = {
        'TOGETHER_API_KEY': 'API ключ Together AI для обработки новостей',
        'DATABASE_URL': 'URL базы данных PostgreSQL',
        'LOG_LEVEL': 'Уровень логирования',
        'MAX_NEWS_PER_CATEGORY': 'Максимальное количество новостей на категорию',
        'NEWS_CACHE_TTL': 'Время жизни кэша новостей в секундах',
        'RSS_TIMEOUT': 'Таймаут для RSS запросов в секундах'
    }
    
    # Проверяем обязательные переменные
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            errors.append(f"❌ {var} не установлен ({description})")
        else:
            # Проверяем формат токена бота
            if var == 'BOT_TOKEN':
                if not value.count(':') == 1 or len(value.split(':')[0]) < 8:
                    errors.append(f"❌ {var} имеет неверный формат")
                else:
                    logger.info(f"✅ {var} установлен корректно")
    
    # Проверяем опциональные переменные
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if not value:
            warnings.append(f"⚠️ {var} не установлен ({description})")
        else:
            logger.info(f"✅ {var} установлен")
    
    # Проверяем специфичные настройки
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        warnings.append(f"⚠️ LOG_LEVEL имеет неверное значение: {log_level}")
    
    # Проверяем числовые значения
    numeric_vars = ['MAX_NEWS_PER_CATEGORY', 'NEWS_CACHE_TTL', 'RSS_TIMEOUT']
    for var in numeric_vars:
        value = os.getenv(var)
        if value:
            try:
                int(value)
            except ValueError:
                warnings.append(f"⚠️ {var} должен быть числом, получено: {value}")
    
    # Выводим результаты
    if errors:
        logger.error("Найдены критические ошибки конфигурации:")
        for error in errors:
            logger.error(error)
        return False
    
    if warnings:
        logger.warning("Найдены предупреждения конфигурации:")
        for warning in warnings:
            logger.warning(warning)
    
    logger.info("✅ Конфигурация валидна!")
    return True

def print_config_info():
    """Выводит информацию о текущей конфигурации"""
    logger.info("📋 Текущая конфигурация:")
    
    # Безопасно показываем конфигурацию (скрываем токены)
    config_vars = [
        'BOT_TOKEN', 'TOGETHER_API_KEY', 'DATABASE_URL',
        'LOG_LEVEL', 'MAX_NEWS_PER_CATEGORY', 'NEWS_CACHE_TTL',
        'RSS_TIMEOUT', 'ENVIRONMENT'
    ]
    
    for var in config_vars:
        value = os.getenv(var, 'не установлено')
        
        # Скрываем чувствительные данные
        if var in ['BOT_TOKEN', 'TOGETHER_API_KEY', 'DATABASE_URL'] and value != 'не установлено':
            if len(value) > 10:
                value = value[:6] + '...' + value[-4:]
            else:
                value = '***'
        
        logger.info(f"  {var}: {value}")

if __name__ == "__main__":
    print_config_info()
    
    if not validate_config():
        sys.exit(1)
    
    logger.info("🎉 Конфигурация готова к использованию!")
