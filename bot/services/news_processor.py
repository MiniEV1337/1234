import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Optional
from bot.utils.rss_parser import parse_multiple_feeds
from bot.utils.together_api import together_api
from bot.utils.news_cache import news_cache
from bot.data.rss_feeds import RSS_FEEDS

logger = logging.getLogger(__name__)

class NewsProcessor:
    def __init__(self):
        self.processing_lock = asyncio.Lock()
        
    async def process_category_news(self, category: str, force_update: bool = False) -> bool:
        """Обрабатывает новости для конкретной категории"""
        async with self.processing_lock:
            try:
                logger.info(f"🔄 Начинаем обработку категории: {category}")
                
                if category not in RSS_FEEDS:
                    logger.error(f"❌ Категория {category} не найдена в RSS_FEEDS")
                    return False
                
                # Получаем RSS ленты для категории
                feeds = RSS_FEEDS[category]
                feed_urls = list(feeds.values())
                
                logger.info(f"📡 Парсинг {len(feed_urls)} RSS лент для категории {category}")
                
                # Парсим все RSS ленты параллельно
                all_news = await parse_multiple_feeds(feed_urls, max_items_per_feed=5)
                
                if not all_news:
                    logger.warning(f"⚠️ Не получено новостей для категории {category}")
                    return False
                
                logger.info(f"📰 Получено {len(all_news)} новостей для категории {category}")
                
                # Обрабатываем новости через AI
                processed_news = await self._process_news_with_ai(all_news, category)
                
                if processed_news:
                    # Сохраняем в кеш
                    success = await news_cache.save_news(category, processed_news)
                    if success:
                        logger.info(f"✅ Категория {category} успешно обработана и сохранена")
                        return True
                    else:
                        logger.error(f"❌ Ошибка сохранения новостей для категории {category}")
                        return False
                else:
                    logger.error(f"❌ Не удалось обработать новости для категории {category}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Критическая ошибка обработки категории {category}: {e}")
                return False
    
    async def _process_news_with_ai(self, news_list: List[Dict], category: str) -> List[Dict]:
        """Обрабатывает новости через AI как редактор"""
        try:
            logger.info(f"🤖 Обрабатываем {len(news_list)} новостей для категории {category}")
            
            # Обрабатываем новости батчами
            batch_size = 3  # Уменьшаем размер батча для стабильности
            processed_news = []
            
            for i in range(0, len(news_list), batch_size):
                batch = news_list[i:i + batch_size]
                
                logger.info(f"🔄 Обрабатываем батч {i//batch_size + 1} из {(len(news_list) + batch_size - 1)//batch_size}")
                
                # Обрабатываем батч через AI
                batch_results = await together_api.process_news_batch(batch)
                
                if batch_results:
                    processed_news.extend(batch_results)
                    logger.info(f"✅ Обработано {len(batch_results)} новостей в батче")
                else:
                    logger.warning(f"⚠️ Батч не обработан, добавляем оригиналы")
                    # Добавляем необработанные новости
                    for news_item in batch:
                        processed_news.append({
                            **news_item,
                            'content': news_item.get('summary', ''),
                            'ai_processed': False
                        })
                
                # Пауза между батчами
                await asyncio.sleep(2)
            
            logger.info(f"✅ Обработано {len(processed_news)} из {len(news_list)} новостей для категории {category}")
            return processed_news
            
        except Exception as e:
            logger.error(f"❌ Ошибка AI обработки для категории {category}: {e}")
            # Возвращаем необработанные новости
            return [{
                **news_item,
                'content': news_item.get('summary', ''),
                'ai_processed': False,
                'error': str(e)
            } for news_item in news_list]
    
    async def process_all_categories(self) -> Dict[str, bool]:
        """Обрабатывает все категории новостей"""
        results = {}
        
        logger.info("🚀 Начинаем полную обработку всех категорий новостей")
        
        for category in RSS_FEEDS.keys():
            try:
                logger.info(f"🔄 Обрабатываем категорию: {category}")
                success = await self.process_category_news(category)
                results[category] = success
                
                if success:
                    logger.info(f"✅ Категория {category} успешно обработана")
                else:
                    logger.error(f"❌ Ошибка обработки категории {category}")
                
                # Пауза между категориями
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Критическая ошибка обработки категории {category}: {e}")
                results[category] = False
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        logger.info(f"🏁 Полная обработка завершена: {successful}/{total} категорий успешно обработано")
        
        return results

# Создаем глобальный экземпляр процессора
news_processor = NewsProcessor()
