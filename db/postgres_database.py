"""
Модуль для работы с PostgreSQL базой данных
"""

import asyncpg
import logging
from typing import List, Tuple, Optional
from .models import *

logger = logging.getLogger(__name__)


class PostgresDatabase:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._pool = None

    async def connect(self):
        """Создание соединения с базой данных"""
        try:
            self._pool = await asyncpg.create_pool(self.database_url)
            await self._create_tables()
            logger.info("PostgreSQL база данных успешно подключена")
        except Exception as e:
            logger.error(f"Ошибка подключения к PostgreSQL: {e}")
            raise

    async def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self._pool:
            await self._pool.close()
            logger.info("Соединение с PostgreSQL закрыто")

    async def _create_tables(self):
        """Создание таблиц в базе данных"""
        try:
            async with self._pool.acquire() as conn:
                # Создаем таблицы
                await conn.execute(CREATE_ENTRIES_TABLE_POSTGRES)
                await conn.execute(CREATE_CUSTOM_CATEGORIES_TABLE_POSTGRES)
                await conn.execute(CREATE_REMINDERS_TABLE_POSTGRES)
                await conn.execute(CREATE_ENTRIES_INDEX_POSTGRES)
                await conn.execute(CREATE_REMINDERS_INDEX_POSTGRES)
            logger.info("Таблицы PostgreSQL созданы/проверены")
        except Exception as e:
            logger.error(f"Ошибка создания таблиц PostgreSQL: {e}")
            raise

    async def add_entry(self, user_id: int, text: str, category: str) -> int:
        """Добавление новой записи"""
        try:
            logger.info(f"Попытка добавления записи: user_id={user_id}, category={category}, text_length={len(text)}")
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    INSERT_ENTRY_POSTGRES, user_id, text, category
                )
                entry_id = row['id']
            logger.info(f"Запись добавлена для пользователя {user_id}, ID: {entry_id}")
            return entry_id
        except Exception as e:
            logger.error(f"Ошибка добавления записи: {e}")
            return None

    async def get_today_entries(self, user_id: int) -> List[Tuple[str, str, str]]:
        """Получение записей за сегодня"""
        try:
            logger.info(f"Запрос записей за сегодня для пользователя {user_id}")
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(GET_TODAY_ENTRIES_POSTGRES, user_id)
                entries = [(row['text'], row['category'], str(row['datetime'])) for row in rows]
            logger.info(f"Получено {len(entries)} записей за сегодня для пользователя {user_id}")
            for entry in entries:
                logger.debug(f"Запись: {entry}")
            return entries
        except Exception as e:
            logger.error(f"Ошибка получения записей за сегодня: {e}")
            return []

    async def get_entries_by_date(self, user_id: int, date: str) -> List[Tuple[str, str, str]]:
        """Получение записей за конкретную дату"""
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(GET_ENTRIES_BY_DATE_POSTGRES, user_id, date)
                entries = [(row['text'], row['category'], str(row['datetime'])) for row in rows]
            logger.info(f"Получено {len(entries)} записей за {date} для пользователя {user_id}")
            return entries
        except Exception as e:
            logger.error(f"Ошибка получения записей за дату: {e}")
            return []

    async def search_entries(self, user_id: int, search_term: str) -> List[Tuple[str, str, str]]:
        """Поиск записей по ключевому слову"""
        try:
            search_pattern = f"%{search_term}%"
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(SEARCH_ENTRIES_POSTGRES, user_id, search_pattern)
                entries = [(row['text'], row['category'], str(row['datetime'])) for row in rows]
            logger.info(f"Найдено {len(entries)} записей по запросу '{search_term}' для пользователя {user_id}")
            return entries
        except Exception as e:
            logger.error(f"Ошибка поиска записей: {e}")
            return []

    async def add_custom_category(self, user_id: int, name: str, keywords: str) -> bool:
        """Добавление пользовательской категории"""
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(INSERT_CUSTOM_CATEGORY_POSTGRES, user_id, name, keywords)
            logger.info(f"Пользовательская категория '{name}' добавлена для пользователя {user_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления пользовательской категории: {e}")
            return False

    async def get_custom_categories(self, user_id: int) -> List[Tuple[str, str]]:
        """Получение пользовательских категорий пользователя"""
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(GET_CUSTOM_CATEGORIES_POSTGRES, user_id)
                categories = [(row['name'], row['keywords']) for row in rows]
            logger.info(f"Получено {len(categories)} пользовательских категорий для пользователя {user_id}")
            return categories
        except Exception as e:
            logger.error(f"Ошибка получения пользовательских категорий: {e}")
            return []

    async def get_all_custom_categories(self) -> List[Tuple[int, str, str]]:
        """Получение всех пользовательских категорий (для категоризатора)"""
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(GET_ALL_CUSTOM_CATEGORIES_POSTGRES)
                categories = [(row['user_id'], row['name'], row['keywords']) for row in rows]
            return categories
        except Exception as e:
            logger.error(f"Ошибка получения всех пользовательских категорий: {e}")
            return []

    async def add_reminder(self, user_id: int, entry_id: int, text: str, reminder_time: str) -> bool:
        """Добавление напоминания"""
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(INSERT_REMINDER_POSTGRES, user_id, entry_id, text, reminder_time)
            logger.info(f"Напоминание добавлено для пользователя {user_id} на {reminder_time}")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления напоминания: {e}")
            return False

    async def get_pending_reminders(self) -> List[Tuple[int, int, str, str]]:
        """Получение всех ожидающих напоминаний"""
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(GET_PENDING_REMINDERS_POSTGRES)
                reminders = [(row['id'], row['user_id'], row['text'], str(row['reminder_time'])) for row in rows]
            return reminders
        except Exception as e:
            logger.error(f"Ошибка получения напоминаний: {e}")
            return []

    async def mark_reminder_sent(self, reminder_id: int) -> bool:
        """Отметить напоминание как отправленное"""
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(MARK_REMINDER_SENT_POSTGRES, reminder_id)
            logger.info(f"Напоминание {reminder_id} отмечено как отправленное")
            return True
        except Exception as e:
            logger.error(f"Ошибка отметки напоминания: {e}")
            return False

    async def get_user_reminders(self, user_id: int) -> List[Tuple[int, str, str, bool]]:
        """Получение напоминаний пользователя"""
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(GET_USER_REMINDERS_POSTGRES, user_id)
                reminders = [(row['id'], row['text'], str(row['reminder_time']), row['is_sent']) for row in rows]
            logger.info(f"Получено {len(reminders)} напоминаний для пользователя {user_id}")
            return reminders
        except Exception as e:
            logger.error(f"Ошибка получения напоминаний пользователя: {e}")
            return [] 