FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем необходимые директории
RUN mkdir -p /app/logs /app/cache/news /app/bot

# Копируем код приложения
COPY . .

# Устанавливаем права на выполнение для скриптов
RUN chmod +x docker/entrypoint.sh

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app
USER botuser

# Открываем порт для веб-интерфейса (если нужен)
EXPOSE 8000

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Точка входа
ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["python", "bot/main.py"]
