"""
Модуль для автоматической категоризации текста
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# Системные категории с ключевыми словами
CATEGORIES = {
    "Задачи": ["нужно", "сделать", "завтра", "встретиться", "отправить", "купить", "записаться", "позвонить"],
    "Идеи": ["идея", "можно было бы", "было бы круто", "попробовать", "интересно", "креативно", "новое"],
    "Вопросы": ["почему", "как", "зачем", "что будет если", "когда", "где", "кто", "?"],
    "Тревоги": ["боюсь", "волнуюсь", "напрягает", "переживаю", "тревога", "страх", "беспокоюсь", "неуверен"],
    "Факты": ["цитата", "запомни", "факт", "интересно", "узнал", "прочитал", "услышал"],
    "Планы": ["мечтаю", "планирую", "цель", "хочу", "буду", "собираюсь", "намерен"],
    "Прочее": []
}

# Эмодзи для категорий
CATEGORY_EMOJIS = {
    "Задачи": "📋",
    "Идеи": "💡",
    "Вопросы": "❓",
    "Тревоги": "😰",
    "Факты": "📚",
    "Планы": "🎯",
    "Прочее": "📝"
}


class Categorizer:
    def __init__(self, database=None):
        self.database = database
        self._custom_categories_cache = {}
        self._cache_updated = False

    async def _load_custom_categories(self):
        """Загрузка пользовательских категорий из базы данных"""
        if not self.database or self._cache_updated:
            return

        try:
            custom_categories = await self.database.get_all_custom_categories()
            self._custom_categories_cache.clear()
            
            for user_id, name, keywords in custom_categories:
                if user_id not in self._custom_categories_cache:
                    self._custom_categories_cache[user_id] = {}
                self._custom_categories_cache[user_id][name] = [
                    kw.strip().lower() for kw in keywords.split(',')
                ]
            
            self._cache_updated = True
            logger.info("Пользовательские категории загружены в кэш")
        except Exception as e:
            logger.error(f"Ошибка загрузки пользовательских категорий: {e}")

    def _check_keywords(self, text: str, keywords: List[str]) -> bool:
        """Проверка наличия ключевых слов в тексте"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)

    async def categorize(self, text: str, user_id: int = None) -> Tuple[str, str]:
        """
        Категоризация текста
        
        Args:
            text: Текст для категоризации
            user_id: ID пользователя для проверки пользовательских категорий
            
        Returns:
            Tuple[str, str]: (название_категории, эмодзи_категории)
        """
        await self._load_custom_categories()
        
        # Сначала проверяем пользовательские категории
        if user_id and user_id in self._custom_categories_cache:
            for category_name, keywords in self._custom_categories_cache[user_id].items():
                if self._check_keywords(text, keywords):
                    logger.info(f"Текст категоризирован как пользовательская категория '{category_name}'")
                    return category_name, "🔧"  # Эмодзи для пользовательских категорий

        # Затем проверяем системные категории
        for category_name, keywords in CATEGORIES.items():
            if category_name == "Прочее":
                continue  # Пропускаем "Прочее" - это категория по умолчанию
                
            if self._check_keywords(text, keywords):
                emoji = CATEGORY_EMOJIS.get(category_name, "📝")
                logger.info(f"Текст категоризирован как '{category_name}'")
                return category_name, emoji

        # Если ничего не найдено, возвращаем "Прочее"
        logger.info("Текст категоризирован как 'Прочее'")
        return "Прочее", CATEGORY_EMOJIS["Прочее"]

    def get_all_categories(self) -> Dict[str, List[str]]:
        """Получение всех системных категорий"""
        return CATEGORIES.copy()

    def get_category_emoji(self, category: str) -> str:
        """Получение эмодзи для категории"""
        return CATEGORY_EMOJIS.get(category, "📝")

    async def invalidate_cache(self):
        """Инвалидация кэша пользовательских категорий"""
        self._cache_updated = False
        logger.info("Кэш пользовательских категорий инвалидирован") 