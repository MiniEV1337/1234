import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from bot.config import config

logger = logging.getLogger(__name__)

class NewsCache:
    def __init__(self):
        self.archive_path = Path(config.NEWS_ARCHIVE_PATH)
        self.max_age_hours = config.NEWS_CACHE_HOURS
        self.lock = asyncio.Lock()
        
        # Создаем директорию архива если не существует
        self.archive_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Архив новостей: {self.archive_path}")
    
    def _get_category_file(self, category: str) -> Path:
        """Получает путь к файлу категории"""
        return self.archive_path / f"{category}.json"
    
    def _get_daily_archive_file(self, date: datetime) -> Path:
        """Получает путь к дневному архиву"""
        date_str = date.strftime("%Y-%m-%d")
        return self.archive_path / "daily" / f"{date_str}.json"
    
    async def save_news(self, category: str, news_list: List[Dict]) -> bool:
        """Сохраняет новости категории"""
        async with self.lock:
            try:
                category_file = self._get_category_file(category)
                
                # Подготавливаем данные для сохранения
                cache_data = {
                    'category': category,
                    'updated_at': datetime.now().isoformat(),
                    'news_count': len(news_list),
                    'news': news_list
                }
                
                # Сохраняем в файл категории
                with open(category_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
                # Также сохраняем в дневной архив
                await self._save_to_daily_archive(news_list)
                
                logger.info(f"💾 Сохранено {len(news_list)} новостей для категории {category}")
                return True
                
            except Exception as e:
                logger.error(f"❌ Ошибка сохранения новостей {category}: {e}")
                return False
    
    async def _save_to_daily_archive(self, news_list: List[Dict]):
        """Сохраняет новости в дневной архив"""
        try:
            today = datetime.now()
            daily_file = self._get_daily_archive_file(today)
            
            # Создаем директорию если не существует
            daily_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Загружаем существующий архив или создаем новый
            daily_data = []
            if daily_file.exists():
                with open(daily_file, 'r', encoding='utf-8') as f:
                    daily_data = json.load(f)
            
            # Добавляем новые новости (избегаем дубликатов)
            existing_ids = {item.get('id') for item in daily_data}
            new_items = [item for item in news_list if item.get('id') not in existing_ids]
            
            if new_items:
                daily_data.extend(new_items)
                
                # Сортируем по времени публикации
                daily_data.sort(key=lambda x: x.get('published_timestamp', 0), reverse=True)
                
                # Сохраняем обновленный архив
                with open(daily_file, 'w', encoding='utf-8') as f:
                    json.dump(daily_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"📅 Добавлено {len(new_items)} новостей в дневной архив")
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в дневной архив: {e}")
    
    async def load_news(self, category: str) -> Optional[List[Dict]]:
        """Загружает новости категории"""
        try:
            category_file = self._get_category_file(category)
            
            if not category_file.exists():
                logger.warning(f"⚠️ Файл категории {category} не найден")
                return None
            
            with open(category_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Проверяем актуальность кеша
            updated_at = datetime.fromisoformat(cache_data.get('updated_at', ''))
            if datetime.now() - updated_at > timedelta(hours=self.max_age_hours):
                logger.warning(f"⚠️ Кеш категории {category} устарел")
                return None
            
            news_list = cache_data.get('news', [])
            logger.info(f"📰 Загружено {len(news_list)} новостей для категории {category}")
            return news_list
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки новостей {category}: {e}")
            return None
    
    async def get_latest_news(self, limit: int = 10) -> List[Dict]:
        """Получает последние новости из всех категорий"""
        try:
            all_news = []
            
            # Собираем новости из всех категорий
            for category_file in self.archive_path.glob("*.json"):
                if category_file.name == "cache_stats.json":
                    continue
                
                try:
                    with open(category_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    news_list = cache_data.get('news', [])
                    all_news.extend(news_list)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка чтения {category_file}: {e}")
                    continue
            
            # Сортируем по времени публикации и берем последние
            all_news.sort(key=lambda x: x.get('published_timestamp', 0), reverse=True)
            latest_news = all_news[:limit]
            
            logger.info(f"📰 Получено {len(latest_news)} последних новостей")
            return latest_news
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения последних новостей: {e}")
            return []
    
    async def cleanup_old_news(self):
        """Очищает устаревшие новости"""
        async with self.lock:
            try:
                logger.info("🧹 Начинаем очистку устаревших новостей")
                
                cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
                cleaned_files = 0
                
                # Очищаем файлы категорий
                for category_file in self.archive_path.glob("*.json"):
                    if category_file.name == "cache_stats.json":
                        continue
                    
                    try:
                        with open(category_file, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        updated_at = datetime.fromisoformat(cache_data.get('updated_at', ''))
                        
                        if updated_at < cutoff_time:
                            category_file.unlink()
                            cleaned_files += 1
                            logger.info(f"🗑️ Удален устаревший файл: {category_file.name}")
                    
                    except Exception as e:
                        logger.warning(f"⚠️ Ошибка обработки {category_file}: {e}")
                
                # Очищаем старые дневные архивы
                daily_dir = self.archive_path / "daily"
                if daily_dir.exists():
                    for daily_file in daily_dir.glob("*.json"):
                        try:
                            # Извлекаем дату из имени файла
                            date_str = daily_file.stem
                            file_date = datetime.strptime(date_str, "%Y-%m-%d")
                            
                            if file_date < cutoff_time:
                                daily_file.unlink()
                                cleaned_files += 1
                                logger.info(f"🗑️ Удален старый дневной архив: {daily_file.name}")
                        
                        except Exception as e:
                            logger.warning(f"⚠️ Ошибка обработки дневного архива {daily_file}: {e}")
                
                logger.info(f"✅ Очистка завершена, удалено файлов: {cleaned_files}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка очистки: {e}")
    
    async def get_cache_stats(self) -> Dict:
        """Получает статистику кеша"""
        try:
            stats = {
                'archive_location': str(self.archive_path),
                'total_news': 0,
                'categories': {},
                'daily_archives': 0,
                'cache_size_mb': 0
            }
            
            # Статистика по категориям
            for category_file in self.archive_path.glob("*.json"):
                if category_file.name == "cache_stats.json":
                    continue
                
                try:
                    with open(category_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    category = cache_data.get('category', category_file.stem)
                    news_count = cache_data.get('news_count', 0)
                    updated_at = cache_data.get('updated_at', 'Неизвестно')
                    
                    stats['categories'][category] = {
                        'count': news_count,
                        'last_updated': updated_at
                    }
                    stats['total_news'] += news_count
                    
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка чтения статистики {category_file}: {e}")
            
            # Статистика дневных архивов
            daily_dir = self.archive_path / "daily"
            if daily_dir.exists():
                stats['daily_archives'] = len(list(daily_dir.glob("*.json")))
            
            # Размер кеша
            total_size = sum(f.stat().st_size for f in self.archive_path.rglob("*.json"))
            stats['cache_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики кеша: {e}")
            return {'error': str(e)}

# Создаем глобальный экземпляр кеша
news_cache = NewsCache()
