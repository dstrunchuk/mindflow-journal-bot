"""
Модуль для работы с базой данных SQLite
"""

import aiosqlite
import logging
from typing import List, Tuple, Optional
from .models import *

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection = None

    async def connect(self):
        """Создание соединения с базой данных"""
        try:
            self._connection = await aiosqlite.connect(self.db_path)
            await self._connection.execute("PRAGMA foreign_keys = ON")
            await self._create_tables()
            logger.info(f"База данных успешно подключена: {self.db_path}")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

    async def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self._connection:
            await self._connection.close()
            logger.info("Соединение с базой данных закрыто")

    async def _create_tables(self):
        """Создание таблиц в базе данных"""
        try:
            await self._connection.execute(CREATE_ENTRIES_TABLE)
            await self._connection.execute(CREATE_CUSTOM_CATEGORIES_TABLE)
            await self._connection.execute(CREATE_REMINDERS_TABLE)
            await self._connection.execute(CREATE_ENTRIES_INDEX)
            await self._connection.execute(CREATE_REMINDERS_INDEX)
            await self._connection.commit()
            logger.info("Таблицы базы данных созданы/проверены")
        except Exception as e:
            logger.error(f"Ошибка создания таблиц: {e}")
            raise

    async def add_entry(self, user_id: int, text: str, category: str) -> int:
        """Добавление новой записи"""
        try:
            logger.info(f"Попытка добавления записи: user_id={user_id}, category={category}, text_length={len(text)}")
            cursor = await self._connection.execute(INSERT_ENTRY, (user_id, text, category))
            await self._connection.commit()
            entry_id = cursor.lastrowid
            logger.info(f"Запись добавлена для пользователя {user_id}, ID: {entry_id}")
            return entry_id
        except Exception as e:
            logger.error(f"Ошибка добавления записи: {e}")
            return None

    async def get_today_entries(self, user_id: int) -> List[Tuple[str, str, str]]:
        """Получение записей за сегодня"""
        try:
            logger.info(f"Запрос записей за сегодня для пользователя {user_id}")
            cursor = await self._connection.execute(GET_TODAY_ENTRIES, (user_id,))
            entries = await cursor.fetchall()
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
            cursor = await self._connection.execute(GET_ENTRIES_BY_DATE, (user_id, date))
            entries = await cursor.fetchall()
            logger.info(f"Получено {len(entries)} записей за {date} для пользователя {user_id}")
            return entries
        except Exception as e:
            logger.error(f"Ошибка получения записей за дату: {e}")
            return []

    async def search_entries(self, user_id: int, search_term: str) -> List[Tuple[str, str, str]]:
        """Поиск записей по ключевому слову"""
        try:
            search_pattern = f"%{search_term}%"
            cursor = await self._connection.execute(SEARCH_ENTRIES, (user_id, search_pattern))
            entries = await cursor.fetchall()
            logger.info(f"Найдено {len(entries)} записей по запросу '{search_term}' для пользователя {user_id}")
            return entries
        except Exception as e:
            logger.error(f"Ошибка поиска записей: {e}")
            return []

    async def add_custom_category(self, user_id: int, name: str, keywords: str) -> bool:
        """Добавление пользовательской категории"""
        try:
            await self._connection.execute(INSERT_CUSTOM_CATEGORY, (user_id, name, keywords))
            await self._connection.commit()
            logger.info(f"Пользовательская категория '{name}' добавлена для пользователя {user_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления пользовательской категории: {e}")
            return False

    async def get_custom_categories(self, user_id: int) -> List[Tuple[str, str]]:
        """Получение пользовательских категорий пользователя"""
        try:
            cursor = await self._connection.execute(GET_CUSTOM_CATEGORIES, (user_id,))
            categories = await cursor.fetchall()
            logger.info(f"Получено {len(categories)} пользовательских категорий для пользователя {user_id}")
            return categories
        except Exception as e:
            logger.error(f"Ошибка получения пользовательских категорий: {e}")
            return []

    async def get_all_custom_categories(self) -> List[Tuple[int, str, str]]:
        """Получение всех пользовательских категорий (для категоризатора)"""
        try:
            cursor = await self._connection.execute(GET_ALL_CUSTOM_CATEGORIES)
            categories = await cursor.fetchall()
            return categories
        except Exception as e:
            logger.error(f"Ошибка получения всех пользовательских категорий: {e}")
            return []

    async def add_reminder(self, user_id: int, entry_id: int, text: str, reminder_time: str) -> bool:
        """Добавление напоминания"""
        try:
            await self._connection.execute(INSERT_REMINDER, (user_id, entry_id, text, reminder_time))
            await self._connection.commit()
            logger.info(f"Напоминание добавлено для пользователя {user_id} на {reminder_time}")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления напоминания: {e}")
            return False

    async def get_pending_reminders(self) -> List[Tuple[int, int, str, str]]:
        """Получение всех ожидающих напоминаний"""
        try:
            cursor = await self._connection.execute(GET_PENDING_REMINDERS)
            reminders = await cursor.fetchall()
            return reminders
        except Exception as e:
            logger.error(f"Ошибка получения напоминаний: {e}")
            return []

    async def mark_reminder_sent(self, reminder_id: int) -> bool:
        """Отметить напоминание как отправленное"""
        try:
            await self._connection.execute(MARK_REMINDER_SENT, (reminder_id,))
            await self._connection.commit()
            logger.info(f"Напоминание {reminder_id} отмечено как отправленное")
            return True
        except Exception as e:
            logger.error(f"Ошибка отметки напоминания: {e}")
            return False

    async def get_user_reminders(self, user_id: int) -> List[Tuple[int, str, str, bool]]:
        """Получение напоминаний пользователя"""
        try:
            cursor = await self._connection.execute(GET_USER_REMINDERS, (user_id,))
            reminders = await cursor.fetchall()
            logger.info(f"Получено {len(reminders)} напоминаний для пользователя {user_id}")
            return reminders
        except Exception as e:
            logger.error(f"Ошибка получения напоминаний пользователя: {e}")
            return [] 