import re
import html
from typing import Dict, Optional
from urllib.parse import urlparse

def clean_html_entities(text: str) -> str:
    """Очищает HTML entities из текста"""
    if not text:
        return ""
    
    # Сначала используем стандартный html.unescape
    text = html.unescape(text)
    
    # Дополнительные замены для специфичных случаев
    replacements = {
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
        '&#8230;': '…',
        '&nbsp;': ' '
    }
    
    for entity, replacement in replacements.items():
        text = text.replace(entity, replacement)
    
    return text

def remove_emoji_from_category(category_name: str) -> str:
    """Убирает эмодзи из названия категории"""
    # Убираем эмодзи и лишние пробелы
    clean_name = re.sub(r'[^\w\s]', '', category_name).strip()
    return clean_name

def validate_url(url: str) -> bool:
    """Проверяет валидность URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def truncate_text(text: str, max_length: int = 4000) -> str:
    """Обрезает текст до максимальной длины для Telegram"""
    if len(text) <= max_length:
        return text
    
    # Обрезаем и добавляем многоточие
    truncated = text[:max_length - 3]
    
    # Пытаемся обрезать по последнему предложению
    last_sentence = truncated.rfind('.')
    if last_sentence > max_length * 0.8:  # Если предложение не слишком короткое
        truncated = truncated[:last_sentence + 1]
    
    return truncated + '...'

def escape_markdown(text: str) -> str:
    """Экранирует специальные символы для Markdown"""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def format_processed_news(processed_news: Dict, source: str, image_url: Optional[str] = None) -> str:
    """Форматирует обработанную новость для отправки в Telegram"""
    try:
        title = clean_html_entities(processed_news.get('title', 'Без заголовка'))
        summary = clean_html_entities(processed_news.get('summary', 'Нет описания'))
        hashtags = processed_news.get('hashtags', [])
        
        # Ограничиваем длину заголовка
        if len(title) > 200:
            title = title[:197] + '...'
        
        # Ограничиваем длину описания
        summary = truncate_text(summary, 3000)
        
        # Формируем текст новости
        news_text = f"<b>{title}</b>\n\n"
        news_text += f"{summary}\n\n"
        
        # Добавляем источник
        if source and source != 'Неизвестный источник':
            news_text += f"📰 <i>{source}</i>\n"
        
        # Добавляем хэштеги
        if hashtags:
            hashtags_text = ' '.join(hashtags[:5])  # Максимум 5 хэштегов
            news_text += f"\n{hashtags_text}"
        
        # Проверяем общую длину для Telegram (лимит 4096 символов)
        news_text = truncate_text(news_text, 4000)
        
        return news_text
        
    except Exception as e:
        return f"❌ Ошибка форматирования новости: {str(e)}"

def clean_filename(filename: str) -> str:
    """Очищает имя файла от недопустимых символов"""
    # Убираем недопустимые символы для имени файла
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Ограничиваем длину
    if len(filename) > 100:
        filename = filename[:100]
    return filename

def format_news_for_storage(news_item: Dict) -> Dict:
    """Форматирует новость для сохранения в кеше"""
    return {
        'id': news_item.get('id', ''),
        'title': clean_html_entities(news_item.get('title', '')),
        'summary': clean_html_entities(news_item.get('summary', '')),
        'link': news_item.get('link', ''),
        'published': news_item.get('published', ''),
        'source_title': clean_html_entities(news_item.get('source_title', '')),
        'image_url': news_item.get('image_url'),
        'processed_at': news_item.get('processed_at', ''),
        'category': news_item.get('category', ''),
        'processed_news': news_item.get('processed_news', {}),
        'language': news_item.get('language', 'unknown')
    }
