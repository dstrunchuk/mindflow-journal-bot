"""
Модуль для фоновой отправки напоминаний
"""

import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from db.database import Database

logger = logging.getLogger(__name__)


class ReminderScheduler:
    def __init__(self, bot: Bot, database: Database):
        self.bot = bot
        self.database = database
        self.is_running = False

    async def start(self):
        """Запуск планировщика напоминаний"""
        self.is_running = True
        logger.info("Планировщик напоминаний запущен")
        
        while self.is_running:
            try:
                await self._check_and_send_reminders()
                await asyncio.sleep(60)  # Проверяем каждую минуту
            except Exception as e:
                logger.error(f"Ошибка в планировщике напоминаний: {e}")
                await asyncio.sleep(60)

    async def stop(self):
        """Остановка планировщика напоминаний"""
        self.is_running = False
        logger.info("Планировщик напоминаний остановлен")

    async def _check_and_send_reminders(self):
        """Проверка и отправка напоминаний"""
        try:
            # Получаем все ожидающие напоминания
            pending_reminders = await self.database.get_pending_reminders()
            
            for reminder_id, user_id, text, reminder_time in pending_reminders:
                try:
                    # Отправляем напоминание
                    message = f"⏰ <b>Напоминание!</b>\n\n{text}"
                    await self.bot.send_message(user_id, message, parse_mode="HTML")
                    
                    # Отмечаем как отправленное
                    await self.database.mark_reminder_sent(reminder_id)
                    
                    logger.info(f"Напоминание {reminder_id} отправлено пользователю {user_id}")
                    
                except Exception as e:
                    logger.error(f"Ошибка отправки напоминания {reminder_id}: {e}")
                    # Если не удалось отправить, оставляем для повторной попытки
                    continue
                    
        except Exception as e:
            logger.error(f"Ошибка проверки напоминаний: {e}") 