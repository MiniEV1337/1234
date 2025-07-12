import os
import sys

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 📦 Добавляем /app в PYTHONPATH, чтобы можно было делать from bot.db.base import Base
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Импорт модели базы и, при необходимости, настроек
from bot.db.base import Base

# Alembic конфигурация
config = context.config

# 👀 Дебаг: выводим, что получили из alembic.ini
sqlalchemy_url = config.get_main_option("sqlalchemy.url")
print(f"🔍 Alembic is using DATABASE_URL = {sqlalchemy_url}")
sqlalchemy_url = config.get_main_option("sqlalchemy.url")
print(f"🔍 Alembic is using DATABASE_URL = {sqlalchemy_url}")

if not sqlalchemy_url or "://" not in sqlalchemy_url:
    raise ValueError("❌ DATABASE_URL is not defined or malformed. Проверь .env.docker и alembic.ini.")

fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    """Запуск миграций в режиме offline"""
    context.configure(
        url=sqlalchemy_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Запуск миграций в режиме online"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
