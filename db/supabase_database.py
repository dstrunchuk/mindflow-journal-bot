"""
Модуль для работы с Supabase через API
"""

import logging
from typing import List, Tuple, Optional
from supabase import create_client, Client
from datetime import datetime, date

logger = logging.getLogger(__name__)


class SupabaseDatabase:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client: Client = None

    async def connect(self):
        """Создание соединения с Supabase"""
        try:
            logger.info(f"Попытка подключения к Supabase: {self.supabase_url}")
            self.client = create_client(self.supabase_url, self.supabase_key)
            
            # Тестируем подключение
            test_result = self.client.table('entries').select('count', count='exact').limit(1).execute()
            logger.info("Supabase клиент успешно подключен")
        except Exception as e:
            logger.error(f"Ошибка подключения к Supabase: {e}")
            logger.error(f"URL: {self.supabase_url}")
            logger.error(f"Key length: {len(self.supabase_key) if self.supabase_key else 0}")
            raise

    async def disconnect(self):
        """Закрытие соединения с Supabase"""
        if self.client:
            # Supabase клиент не требует явного закрытия
            logger.info("Соединение с Supabase закрыто")

    async def add_entry(self, user_id: int, text: str, category: str) -> int:
        """Добавление новой записи"""
        try:
            logger.info(f"Попытка добавления записи: user_id={user_id}, category={category}, text_length={len(text)}")
            
            data = {
                'user_id': user_id,
                'text': text,
                'category': category,
                'datetime': datetime.now().isoformat()
            }
            
            logger.info(f"Данные для вставки: {data}")
            
            result = self.client.table('entries').insert(data).execute()
            logger.info(f"Результат запроса: {result}")
            
            if result.data and len(result.data) > 0:
                entry_id = result.data[0]['id']
                logger.info(f"Запись добавлена для пользователя {user_id}, ID: {entry_id}")
                return entry_id
            else:
                logger.error("Результат запроса пустой")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка добавления записи: {e}")
            logger.error(f"Тип ошибки: {type(e)}")
            return None

    async def get_today_entries(self, user_id: int) -> List[Tuple[str, str, str]]:
        """Получение записей за сегодня"""
        try:
            logger.info(f"Запрос записей за сегодня для пользователя {user_id}")
            
            today = date.today().isoformat()
            result = self.client.table('entries').select('text, category, datetime').eq('user_id', user_id).gte('datetime', today).lt('datetime', f"{today}T23:59:59").order('datetime', desc=True).execute()
            
            entries = [(row['text'], row['category'], row['datetime']) for row in result.data]
            logger.info(f"Получено {len(entries)} записей за сегодня для пользователя {user_id}")
            
            for entry in entries:
                logger.debug(f"Запись: {entry}")
            return entries
        except Exception as e:
            logger.error(f"Ошибка получения записей за сегодня: {e}")
            return []

    async def get_entries_by_date(self, user_id: int, date_str: str) -> List[Tuple[str, str, str]]:
        """Получение записей за конкретную дату"""
        try:
            result = self.client.table('entries').select('text, category, datetime').eq('user_id', user_id).gte('datetime', date_str).lt('datetime', f"{date_str}T23:59:59").order('datetime', desc=True).execute()
            
            entries = [(row['text'], row['category'], row['datetime']) for row in result.data]
            logger.info(f"Получено {len(entries)} записей за {date_str} для пользователя {user_id}")
            return entries
        except Exception as e:
            logger.error(f"Ошибка получения записей за дату: {e}")
            return []

    async def search_entries(self, user_id: int, search_term: str) -> List[Tuple[str, str, str]]:
        """Поиск записей по ключевому слову"""
        try:
            result = self.client.table('entries').select('text, category, datetime').eq('user_id', user_id).ilike('text', f'%{search_term}%').order('datetime', desc=True).execute()
            
            entries = [(row['text'], row['category'], row['datetime']) for row in result.data]
            logger.info(f"Найдено {len(entries)} записей по запросу '{search_term}' для пользователя {user_id}")
            return entries
        except Exception as e:
            logger.error(f"Ошибка поиска записей: {e}")
            return []

    async def add_custom_category(self, user_id: int, name: str, keywords: str) -> bool:
        """Добавление пользовательской категории"""
        try:
            data = {
                'user_id': user_id,
                'name': name,
                'keywords': keywords
            }
            
            self.client.table('custom_categories').upsert(data).execute()
            logger.info(f"Пользовательская категория '{name}' добавлена для пользователя {user_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления пользовательской категории: {e}")
            return False

    async def get_custom_categories(self, user_id: int) -> List[Tuple[str, str]]:
        """Получение пользовательских категорий пользователя"""
        try:
            result = self.client.table('custom_categories').select('name, keywords').eq('user_id', user_id).execute()
            
            categories = [(row['name'], row['keywords']) for row in result.data]
            logger.info(f"Получено {len(categories)} пользовательских категорий для пользователя {user_id}")
            return categories
        except Exception as e:
            logger.error(f"Ошибка получения пользовательских категорий: {e}")
            return []

    async def get_all_custom_categories(self) -> List[Tuple[int, str, str]]:
        """Получение всех пользовательских категорий (для категоризатора)"""
        try:
            result = self.client.table('custom_categories').select('user_id, name, keywords').execute()
            
            categories = [(row['user_id'], row['name'], row['keywords']) for row in result.data]
            return categories
        except Exception as e:
            logger.error(f"Ошибка получения всех пользовательских категорий: {e}")
            return []

    async def add_reminder(self, user_id: int, entry_id: int, text: str, reminder_time: str) -> bool:
        """Добавление напоминания"""
        try:
            data = {
                'user_id': user_id,
                'entry_id': entry_id,
                'text': text,
                'reminder_time': reminder_time,
                'is_sent': False
            }
            
            self.client.table('reminders').insert(data).execute()
            logger.info(f"Напоминание добавлено для пользователя {user_id} на {reminder_time}")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления напоминания: {e}")
            return False

    async def get_pending_reminders(self) -> List[Tuple[int, int, str, str]]:
        """Получение всех ожидающих напоминаний"""
        try:
            now = datetime.now().isoformat()
            result = self.client.table('reminders').select('id, user_id, text, reminder_time').eq('is_sent', False).lte('reminder_time', now).order('reminder_time').execute()
            
            reminders = [(row['id'], row['user_id'], row['text'], row['reminder_time']) for row in result.data]
            return reminders
        except Exception as e:
            logger.error(f"Ошибка получения напоминаний: {e}")
            return []

    async def mark_reminder_sent(self, reminder_id: int) -> bool:
        """Отметить напоминание как отправленное"""
        try:
            self.client.table('reminders').update({'is_sent': True}).eq('id', reminder_id).execute()
            logger.info(f"Напоминание {reminder_id} отмечено как отправленное")
            return True
        except Exception as e:
            logger.error(f"Ошибка отметки напоминания: {e}")
            return False

    async def get_user_reminders(self, user_id: int) -> List[Tuple[int, str, str, bool]]:
        """Получение напоминаний пользователя"""
        try:
            result = self.client.table('reminders').select('id, text, reminder_time, is_sent').eq('user_id', user_id).order('reminder_time', desc=True).execute()
            
            reminders = [(row['id'], row['text'], row['reminder_time'], row['is_sent']) for row in result.data]
            logger.info(f"Получено {len(reminders)} напоминаний для пользователя {user_id}")
            return reminders
        except Exception as e:
            logger.error(f"Ошибка получения напоминаний пользователя: {e}")
            return [] 