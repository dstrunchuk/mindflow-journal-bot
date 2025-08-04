"""
Обработчик команды /reminders
"""

import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("reminders"))
async def cmd_reminders(message: Message, database):
    """Обработчик команды /reminders - показать напоминания пользователя"""
    try:
        user_id = message.from_user.id
        reminders = await database.get_user_reminders(user_id)
        
        if not reminders:
            await message.answer("⏰ У вас пока нет напоминаний.\n\nСоздайте напоминание, написав задачу с указанием времени:\n• через 10 минут нужно встретить друга\n• завтра в 9:00 совещание\n• через час позвонить маме")
            return
            
        # Формируем ответ
        response = "⏰ <b>Ваши напоминания:</b>\n\n"
        
        for i, (reminder_id, text, reminder_time, is_sent) in enumerate(reminders[:10], 1):  # Показываем первые 10
            # Парсим время
            try:
                dt = datetime.strptime(reminder_time, '%Y-%m-%d %H:%M:%S')
                time_str = dt.strftime('%d.%m %H:%M')
                status = "✅" if is_sent else "⏳"
            except:
                time_str = reminder_time
                status = "❓"
            
            # Обрезаем длинный текст
            display_text = text[:100] + "..." if len(text) > 100 else text
            
            response += f"{i}. {status} <b>{time_str}</b>\n"
            response += f"   {display_text}\n\n"
        
        if len(reminders) > 10:
            response += f"... и ещё {len(reminders) - 10} напоминаний"
        
        response += "\n💡 <b>Как создать напоминание:</b>\n"
        response += "Напишите задачу с указанием времени:\n"
        response += "• через 10 минут нужно встретить друга\n"
        response += "• завтра в 9:00 совещание\n"
        response += "• через час позвонить маме"
        
        await message.answer(response, parse_mode="HTML")
        logger.info(f"Пользователю {user_id} показаны напоминания ({len(reminders)} штук)")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /reminders: {e}")
        await message.answer("Произошла ошибка при получении напоминаний. Попробуйте позже.") 