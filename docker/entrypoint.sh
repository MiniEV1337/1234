#!/bin/bash

# Функция для логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "🚀 Запуск новостного бота..."

# Проверяем обязательные переменные окружения
if [ -z "$BOT_TOKEN" ] && [ -z "$TELEGRAM_TOKEN" ]; then
    log "❌ ОШИБКА: Не установлен BOT_TOKEN или TELEGRAM_TOKEN"
    exit 1
fi

if [ -z "$TOGETHER_API_KEY" ]; then
    log "❌ ОШИБКА: Не установлен TOGETHER_API_KEY"
    exit 1
fi

# Создаем необходимые директории
mkdir -p /app/logs /app/cache/news

# Проверяем доступность директорий
if [ ! -w "/app/logs" ]; then
    log "❌ ОШИБКА: Нет прав записи в /app/logs"
    exit 1
fi

if [ ! -w "/app/cache/news" ]; then
    log "❌ ОШИБКА: Нет прав записи в /app/cache/news"
    exit 1
fi

# Устанавливаем PYTHONPATH
export PYTHONPATH=/app:$PYTHONPATH

# Проверяем Python модули
log "🔍 Проверка зависимостей..."
python -c "
import sys
required_modules = [
    'aiogram', 'aiohttp', 'feedparser', 'asyncio', 
    'logging', 'json', 'datetime', 'pathlib'
]

missing_modules = []
for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f'❌ ОШИБКА: Отсутствуют модули: {missing_modules}')
    sys.exit(1)
else:
    print('✅ Все зависимости установлены')
"

if [ $? -ne 0 ]; then
    log "❌ Ошибка проверки зависимостей"
    exit 1
fi

# Проверяем конфигурацию
log "⚙️ Проверка конфигурации..."
python -c "
import os
import sys

# Проверяем переменные окружения
bot_token = os.getenv('BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN')
together_key = os.getenv('TOGETHER_API_KEY')
admin_id = os.getenv('ADMIN_ID', '0')

if not bot_token:
    print('❌ BOT_TOKEN не установлен')
    sys.exit(1)

if not together_key:
    print('❌ TOGETHER_API_KEY не установлен')
    sys.exit(1)

if not admin_id.isdigit():
    print('⚠️ ADMIN_ID не является числом, будет использовано значение по умолчанию')

print('✅ Конфигурация корректна')
print(f'🤖 Bot Token: {bot_token[:10]}...')
print(f'🧠 Together API: {together_key[:10]}...')
print(f'👑 Admin ID: {admin_id}')
"

if [ $? -ne 0 ]; then
    log "❌ Ошибка конфигурации"
    exit 1
fi

# Функция для graceful shutdown
cleanup() {
    log "🛑 Получен сигнал остановки..."
    if [ ! -z "$BOT_PID" ]; then
        log "🔄 Остановка бота (PID: $BOT_PID)..."
        kill -TERM "$BOT_PID" 2>/dev/null
        wait "$BOT_PID" 2>/dev/null
    fi
    log "✅ Бот остановлен"
    exit 0
}

# Устанавливаем обработчики сигналов
trap cleanup SIGTERM SIGINT

# Запускаем бота
log "🚀 Запуск основного процесса бота..."

# Запускаем бота в фоне и сохраняем PID
python "$@" &
BOT_PID=$!

log "✅ Бот запущен с PID: $BOT_PID"

# Ждем завершения процесса
wait $BOT_PID
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log "✅ Бот завершил работу корректно"
else
    log "❌ Бот завершил работу с ошибкой (код: $EXIT_CODE)"
fi

exit $EXIT_CODE
