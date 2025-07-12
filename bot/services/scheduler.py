import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from bot.services.news_processor import news_processor
from bot.utils.news_cache import news_cache
from bot.data.rss_feeds import RSS_FEEDS

logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self):
        self.is_running = False
        self.tasks = []
        self.last_full_update = None
        self.last_cleanup = None
        self.category_rotation_index = 0
        
    async def start(self):
        """Запускает планировщик"""
        if self.is_running:
            logger.warning("⚠️ Планировщик уже запущен")
            return
        
        self.is_running = True
        logger.info("🚀 Запуск планировщика новостей")
        
        # Создаем задачи для разных типов обновлений
        self.tasks = [
            asyncio.create_task(self._full_update_loop()),
            asyncio.create_task(self._category_rotation_loop()),
            asyncio.create_task(self._cleanup_loop()),
            asyncio.create_task(self._status_reporter_loop())
        ]
        
        # Ждем завершения всех задач
        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            logger.info("🛑 Планировщик остановлен")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка планировщика: {e}")
        finally:
            self.is_running = False
    
    async def stop(self):
        """Останавливает планировщик"""
        if not self.is_running:
            logger.warning("⚠️ Планировщик уже остановлен")
            return
        
        logger.info("🛑 Остановка планировщика новостей")
        self.is_running = False
        
        # Отменяем все задачи
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Ждем завершения отмены
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        logger.info("✅ Планировщик остановлен")
    
    async def _full_update_loop(self):
        """Цикл полного обновления всех категорий"""
        # Интервал полного обновления (по умолчанию 1 час)
        import os
        interval = int(os.getenv('FULL_UPDATE_INTERVAL', 3600))
        
        logger.info(f"📅 Запуск цикла полного обновления (интервал: {interval} сек)")
        
        # Первое обновление сразу при запуске
        await self._perform_full_update()
        
        while self.is_running:
            try:
                await asyncio.sleep(interval)
                if self.is_running:
                    await self._perform_full_update()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле полного обновления: {e}")
                await asyncio.sleep(60)  # Пауза перед повтором
    
    async def _category_rotation_loop(self):
        """Цикл ротационного обновления категорий"""
        # Интервал ротационного обновления (по умолчанию 30 минут)
        import os
        interval = int(os.getenv('CATEGORY_UPDATE_INTERVAL', 1800))
        
        logger.info(f"🔄 Запуск цикла ротационного обновления (интервал: {interval} сек)")
        
        categories = list(RSS_FEEDS.keys())
        
        while self.is_running:
            try:
                await asyncio.sleep(interval)
                if self.is_running and categories:
                    # Выбираем следующую категорию для обновления
                    category = categories[self.category_rotation_index % len(categories)]
                    self.category_rotation_index += 1
                    
                    logger.info(f"🔄 Ротационное обновление категории: {category}")
                    await news_processor.process_category_news(category)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле ротационного обновления: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_loop(self):
        """Цикл очистки устаревших новостей"""
        # Интервал очистки (по умолчанию 6 часов)
        import os
        interval = int(os.getenv('CLEANUP_INTERVAL', 21600))
        
        logger.info(f"🧹 Запуск цикла очистки (интервал: {interval} сек)")
        
        while self.is_running:
            try:
                await asyncio.sleep(interval)
                if self.is_running:
                    await self._perform_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле очистки: {e}")
                await asyncio.sleep(300)  # 5 минут пауза
    
    async def _status_reporter_loop(self):
        """Цикл отчетов о состоянии"""
        # Интервал отчетов (каждые 2 часа)
        interval = 7200
        
        logger.info(f"📊 Запуск цикла отчетов (интервал: {interval} сек)")
        
        while self.is_running:
            try:
                await asyncio.sleep(interval)
                if self.is_running:
                    await self._generate_status_report()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле отчетов: {e}")
                await asyncio.sleep(300)
    
    async def _perform_full_update(self):
        """Выполняет полное обновление всех категорий"""
        try:
            logger.info("🔄 Начинаем полное обновление всех категорий")
            start_time = datetime.now()
            
            results = await news_processor.process_all_categories()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            self.last_full_update = end_time
            
            logger.info(f"✅ Полное обновление завершено за {duration:.1f} сек: {successful}/{total} категорий")
            
            # Логируем детали
            for category, success in results.items():
                status = "✅" if success else "❌"
                logger.info(f"  {status} {category}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка полного обновления: {e}")
    
    async def _perform_cleanup(self):
        """Выполняет очистку устаревших новостей"""
        try:
            logger.info("🧹 Начинаем очистку устаревших новостей")
            start_time = datetime.now()
            
            await news_cache.cleanup_old_news()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.last_cleanup = end_time
            
            logger.info(f"✅ Очистка завершена за {duration:.1f} сек")
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки: {e}")
    
    async def _generate_status_report(self):
        """Генерирует отчет о состоянии системы"""
        try:
            logger.info("📊 Генерация отчета о состоянии системы")
            
            # Получаем статистику кеша
            stats = await news_cache.get_cache_stats()
            
            logger.info("📊 === ОТЧЕТ О СОСТОЯНИИ СИСТЕМЫ ===")
            logger.info(f"📁 Расположение архива: {stats.get('archive_location', 'Неизвестно')}")
            logger.info(f"📰 Всего новостей в кеше: {stats.get('total_news', 0)}")
            logger.info(f"📂 Категорий: {len(stats.get('categories', {}))}")
            logger.info(f"📅 Дневных архивов: {stats.get('daily_archives', 0)}")
            logger.info(f"💾 Размер кеша: {stats.get('cache_size_mb', 0)} МБ")
            
            if self.last_full_update:
                time_since_update = datetime.now() - self.last_full_update
                logger.info(f"🔄 Последнее полное обновление: {time_since_update.total_seconds()/3600:.1f} часов назад")
            
            if self.last_cleanup:
                time_since_cleanup = datetime.now() - self.last_cleanup
                logger.info(f"🧹 Последняя очистка: {time_since_cleanup.total_seconds()/3600:.1f} часов назад")
            
            # Детали по категориям
            categories = stats.get('categories', {})
            if categories:
                logger.info("📋 Статистика по категориям:")
                for category, info in categories.items():
                    count = info.get('count', 0)
                    last_updated = info.get('last_updated', 'Неизвестно')
                    logger.info(f"  📰 {category}: {count} новостей (обновлено: {last_updated})")
            
            logger.info("📊 === КОНЕЦ ОТЧЕТА ===")
            
        except Exception as e:
            logger.error(f"❌ Ошибка генерации отчета: {e}")
    
    async def force_update_category(self, category: str) -> bool:
        """Принудительно обновляет конкретную категорию"""
        try:
            logger.info(f"🔄 Принудительное обновление категории: {category}")
            success = await news_processor.process_category_news(category, force_update=True)
            
            if success:
                logger.info(f"✅ Категория {category} принудительно обновлена")
            else:
                logger.error(f"❌ Ошибка принудительного обновления категории {category}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка принудительного обновления {category}: {e}")
            return False
    
    async def force_full_update(self) -> Dict[str, bool]:
        """Принудительно обновляет все категории"""
        try:
            logger.info("🔄 Принудительное полное обновление всех категорий")
            return await news_processor.process_all_categories()
        except Exception as e:
            logger.error(f"❌ Критическая ошибка принудительного полного обновления: {e}")
            return {}
    
    async def get_scheduler_status(self) -> Dict:
        """Получает статус планировщика"""
        try:
            status = {
                'is_running': self.is_running,
                'active_tasks': len([t for t in self.tasks if not t.done()]),
                'last_full_update': self.last_full_update.isoformat() if self.last_full_update else None,
                'last_cleanup': self.last_cleanup.isoformat() if self.last_cleanup else None,
                'category_rotation_index': self.category_rotation_index,
                'total_categories': len(RSS_FEEDS),
                'uptime': None
            }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса планировщика: {e}")
            return {'error': str(e)}

# Создаем глобальный экземпляр планировщика
news_scheduler = NewsScheduler()
