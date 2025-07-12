import asyncio
import aiohttp
import feedparser
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import hashlib

logger = logging.getLogger(__name__)

class RSSParser:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = None
        # Настройки фильтрации по времени
        self.max_news_age_hours = 48  # Максимальный возраст новостей
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def clean_html(self, text: str) -> str:
        """Очищает HTML теги и entities из текста"""
        if not text:
            return ""
        
        # Убираем HTML теги
        text = re.sub(r'<[^>]+>', '', text)
        
        # Заменяем HTML entities
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' ',
            '&laquo;': '«',
            '&raquo;': '»',
            '&ldquo;': '"',
            '&rdquo;': '"',
            '&lsquo;': ''',
            '&rsquo;': ''',
            '&mdash;': '—',
            '&ndash;': '–',
            '&hellip;': '…',
            '&#8220;': '"',
            '&#8221;': '"',
            '&#8216;': ''',
            '&#8217;': ''',
            '&#8212;': '—',
            '&#8211;': '–',
            '&#8230;': '…'
        }
        
        for entity, replacement in html_entities.items():
            text = text.replace(entity, replacement)
        
        # Убираем лишние пробелы и переносы
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_image_url(self, entry: Dict, feed_url: str) -> Optional[str]:
        """Извлекает URL изображения из RSS записи"""
        try:
            # Проверяем media:content
            if hasattr(entry, 'media_content') and entry.media_content:
                for media in entry.media_content:
                    if media.get('type', '').startswith('image/'):
                        return media.get('url')
            
            # Проверяем media:thumbnail
            if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                return entry.media_thumbnail[0].get('url')
            
            # Проверяем enclosure
            if hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        return enclosure.get('href')
            
            # Ищем изображения в описании
            content = entry.get('summary', '') or entry.get('description', '')
            if content:
                img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
                if img_match:
                    img_url = img_match.group(1)
                    # Делаем URL абсолютным
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        base_url = f"{urlparse(feed_url).scheme}://{urlparse(feed_url).netloc}"
                        img_url = urljoin(base_url, img_url)
                    return img_url
            
            return None
            
        except Exception as e:
            logger.warning(f"Ошибка извлечения изображения: {e}")
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Парсит дату из различных форматов"""
        if not date_str:
            return None
        
        try:
            # Пробуем feedparser
            parsed_time = feedparser._parse_date(date_str)
            if parsed_time:
                return datetime(*parsed_time[:6])
        except:
            pass
        
        # Пробуем различные форматы вручную
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                # Убираем часовой пояс для простых форматов
                clean_date = re.sub(r'\s*$$[^)]+$$', '', date_str.strip())
                return datetime.strptime(clean_date, fmt.replace('%z', '').replace('%Z', ''))
            except ValueError:
                continue
        
        logger.warning(f"Не удалось распарсить дату: {date_str}")
        return None
    
    def is_news_fresh(self, published_date: Optional[datetime]) -> bool:
        """Проверяет, является ли новость свежей (не старше 48 часов)"""
        if not published_date:
            # Если дата не определена, считаем новость свежей
            return True
        
        now = datetime.now()
        
        # Проверяем максимальный возраст (48 часов)
        max_age = timedelta(hours=self.max_news_age_hours)
        if now - published_date > max_age:
            return False
        
        # Берем все новости от самых свежих до 48 часов назад
        return True
    
    async def parse_feed(self, feed_url: str, max_items: int = 10) -> List[Dict]:
        """Парсит одну RSS ленту с фильтрацией по времени"""
        try:
            async with self.session.get(feed_url) as response:
                if response.status != 200:
                    logger.warning(f"Ошибка загрузки {feed_url}: {response.status}")
                    return []
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                if feed.bozo and feed.bozo_exception:
                    logger.warning(f"Проблема с парсингом {feed_url}: {feed.bozo_exception}")
                
                news_items = []
                
                for entry in feed.entries:
                    try:
                        # Парсим дату публикации
                        published_date = self.parse_date(
                            entry.get('published', '') or 
                            entry.get('updated', '') or 
                            entry.get('pubDate', '')
                        )
                        
                        # Проверяем свежесть новости (не старше 48 часов)
                        if not self.is_news_fresh(published_date):
                            continue
                        
                        # Генерируем уникальный ID
                        news_id = hashlib.md5(
                            (entry.get('link', '') + entry.get('title', '')).encode()
                        ).hexdigest()
                        
                        # Извлекаем данные
                        title = self.clean_html(entry.get('title', ''))
                        summary = self.clean_html(
                            entry.get('summary', '') or 
                            entry.get('description', '') or 
                            entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
                        )
                        
                        # Извлекаем изображение
                        image_url = self.extract_image_url(entry, feed_url)
                        
                        news_item = {
                            'id': news_id,
                            'title': title,
                            'summary': summary,
                            'link': entry.get('link', ''),
                            'published': published_date.isoformat() if published_date else datetime.now().isoformat(),
                            'published_timestamp': published_date.timestamp() if published_date else datetime.now().timestamp(),
                            'source_title': feed.feed.get('title', 'Неизвестный источник'),
                            'image_url': image_url,
                            'feed_url': feed_url
                        }
                        
                        # Проверяем что есть минимальные данные
                        if title and (summary or entry.get('link')):
                            news_items.append(news_item)
                    
                    except Exception as e:
                        logger.warning(f"Ошибка обработки записи из {feed_url}: {e}")
                        continue
                
                # Сортируем по дате публикации (новые сначала)
                news_items.sort(key=lambda x: x['published_timestamp'], reverse=True)
                
                # Ограничиваем количество
                news_items = news_items[:max_items]
                
                logger.info(f"Получено {len(news_items)} свежих новостей из {feed_url}")
                return news_items
                
        except asyncio.TimeoutError:
            logger.error(f"Таймаут при загрузке {feed_url}")
            return []
        except Exception as e:
            logger.error(f"Ошибка парсинга {feed_url}: {e}")
            return []
    
    def remove_duplicates(self, news_list: List[Dict]) -> List[Dict]:
        """Удаляет дубликаты новостей по заголовку и ссылке"""
        seen_items = set()
        unique_news = []
        
        for news in news_list:
            # Создаем уникальный ключ из заголовка и ссылки
            key = (news['title'].lower().strip(), news.get('link', ''))
            if key not in seen_items:
                seen_items.add(key)
                unique_news.append(news)
        
        return unique_news

async def parse_multiple_feeds(feed_urls: List[str], max_items_per_feed: int = 5) -> List[Dict]:
    """Парсит несколько RSS лент параллельно с сортировкой по времени"""
    async with RSSParser() as parser:
        # Создаем задачи для параллельного парсинга
        tasks = [
            parser.parse_feed(url, max_items_per_feed) 
            for url in feed_urls
        ]
        
        # Выполняем все задачи параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Собираем все новости
        all_news = []
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Ошибка при парсинге: {result}")
        
        # Удаляем дубликаты
        unique_news = parser.remove_duplicates(all_news)
        
        # Сортируем по времени публикации (самые свежие сначала)
        unique_news.sort(key=lambda x: x['published_timestamp'], reverse=True)
        
        logger.info(f"Всего получено {len(unique_news)} уникальных свежих новостей")
        return unique_news
