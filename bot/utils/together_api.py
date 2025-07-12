import asyncio
import aiohttp
import logging
from typing import Dict, Optional, List
from bot.config import config

logger = logging.getLogger(__name__)

class TogetherAPI:
    def __init__(self):
        self.api_key = config.TOGETHER_API_KEY
        self.base_url = "https://api.together.xyz/v1"
        self.timeout = config.AI_TIMEOUT_SECONDS
        self.max_retries = config.MAX_RETRIES
        
        # Лимиты для Telegram
        self.max_message_length = config.MAX_MESSAGE_LENGTH  # 4096 символов
        self.max_caption_length = config.MAX_CAPTION_LENGTH  # 1024 символа
    
    async def _make_request(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """Выполняет запрос к Together API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, json=data, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result
                        else:
                            error_text = await response.text()
                            logger.error(f"API ошибка {response.status}: {error_text}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"Таймаут API запроса (попытка {attempt + 1}/{self.max_retries})")
            except Exception as e:
                logger.error(f"Ошибка API запроса (попытка {attempt + 1}/{self.max_retries}): {e}")
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка
        
        return None
    
    def _create_editor_prompt(self, title: str, content: str) -> str:
        """Создает промпт для редактирования новости"""
        return f"""Ты - редактор Telegram новостного канала. Твоя задача - отредактировать новость для публикации в Telegram.

ВАЖНЫЕ ПРАВИЛА:
1. НЕ переводи текст - работай с оригинальным языком
2. НЕ добавляй информацию от себя - работай только с данным текстом
3. НЕ придумывай факты или детали
4. Если статья короткая - НЕ дополняй её
5. Если статья длинная (больше 4000 символов) - сократи, сохранив главный смысл
6. Сохраняй стиль новостной статьи
7. Убирай рекламные вставки и лишнюю информацию
8. Оставляй только суть новости

ИСХОДНАЯ НОВОСТЬ:
Заголовок: {title}
Текст: {content}

Отредактируй эту новость для Telegram канала. Верни результат в формате JSON:
{{
    "title": "отредактированный заголовок",
    "content": "отредактированный текст новости",
    "summary": "краткое описание (1-2 предложения)"
}}"""
    
    async def edit_news_as_editor(self, title: str, content: str) -> Optional[Dict[str, str]]:
        """Редактирует новость как редактор Telegram канала"""
        try:
            # Проверяем длину контента
            if len(content) < 100:
                # Короткая новость - не обрабатываем
                return {
                    'title': title,
                    'content': content,
                    'summary': content[:200] + '...' if len(content) > 200 else content
                }
            
            prompt = self._create_editor_prompt(title, content)
            
            data = {
                "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            }
            
            response = await self._make_request("chat/completions", data)
            
            if not response or 'choices' not in response:
                logger.error("Некорректный ответ от API")
                return None
            
            ai_response = response['choices'][0]['message']['content'].strip()
            
            # Пытаемся извлечь JSON из ответа
            try:
                import json
                import re
                
                # Ищем JSON в ответе
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    result = json.loads(json_str)
                    
                    # Проверяем длину для Telegram
                    edited_title = result.get('title', title)[:200]  # Ограничиваем заголовок
                    edited_content = result.get('content', content)
                    
                    # Если контент слишком длинный для Telegram, сокращаем
                    if len(edited_content) > self.max_message_length - 200:  # Оставляем место для заголовка
                        edited_content = edited_content[:self.max_message_length - 200] + '...'
                    
                    return {
                        'title': edited_title,
                        'content': edited_content,
                        'summary': result.get('summary', edited_content[:200] + '...')
                    }
                else:
                    logger.warning("JSON не найден в ответе AI")
                    return None
                    
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга JSON: {e}")
                logger.debug(f"Ответ AI: {ai_response}")
                return None
            
        except Exception as e:
            logger.error(f"Ошибка редактирования новости: {e}")
            return None
    
    async def process_news_batch(self, news_list: List[Dict]) -> List[Dict]:
        """Обрабатывает батч новостей"""
        processed_news = []
        
        for news_item in news_list:
            try:
                title = news_item.get('title', '')
                content = news_item.get('summary', '') or news_item.get('description', '')
                
                # Редактируем новость
                edited = await self.edit_news_as_editor(title, content)
                
                if edited:
                    # Обновляем новость
                    processed_item = {
                        **news_item,
                        'original_title': title,
                        'original_content': content,
                        'title': edited['title'],
                        'content': edited['content'],
                        'summary': edited['summary'],
                        'ai_processed': True,
                        'processed_at': asyncio.get_event_loop().time()
                    }
                    processed_news.append(processed_item)
                else:
                    # Если обработка не удалась, оставляем оригинал
                    processed_item = {
                        **news_item,
                        'content': content,
                        'summary': content[:200] + '...' if len(content) > 200 else content,
                        'ai_processed': False
                    }
                    processed_news.append(processed_item)
                
                # Небольшая пауза между запросами
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Ошибка обработки новости: {e}")
                # Добавляем необработанную новость
                processed_news.append({
                    **news_item,
                    'content': news_item.get('summary', ''),
                    'ai_processed': False,
                    'error': str(e)
                })
        
        return processed_news
    
    async def test_connection(self) -> bool:
        """Тестирует соединение с API"""
        try:
            data = {
                "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": "Привет! Это тест соединения."
                    }
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
            
            response = await self._make_request("chat/completions", data)
            
            if response and 'choices' in response:
                logger.info("✅ Соединение с Together API успешно")
                return True
            else:
                logger.error("❌ Ошибка соединения с Together API")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования API: {e}")
            return False

# Создаем глобальный экземпляр
together_api = TogetherAPI()
