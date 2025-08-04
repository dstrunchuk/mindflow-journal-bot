"""
Обработчик команды /start
"""

import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    try:
        welcome_text = """👋 Привет! Это MindFlow Journal.

Просто напишите мне всё, что у вас в голове:
– задачи
– мысли  
– тревоги
– идеи

Я всё сохраню и разложу по полочкам 🧠

📋 Доступные команды:
/today — записи за сегодня
/search слово — найти записи
/categories — все категории
/addcategory Название:ключ1,ключ2 — добавить свою категорию
/archive — записи за конкретную дату
/reminders — мои напоминания

⏰ <b>Автоматические напоминания:</b>
Напишите задачу с указанием времени:
• через 10 минут нужно встретить друга
• завтра в 9:00 совещание
• через час позвонить маме

Просто отправьте мне любое сообщение, и я его сохраню! ✨"""

        await message.answer(welcome_text)
        logger.info(f"Пользователь {message.from_user.id} запустил бота")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.") 