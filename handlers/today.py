"""
Обработчик команды /сегодня
"""

import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.categorizer import CATEGORY_EMOJIS

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("today"))
async def cmd_today(message: Message, database):
    """Обработчик команды /today - показать записи за сегодня"""
    try:
        user_id = message.from_user.id
        entries = await database.get_today_entries(user_id)
        
        if not entries:
            await message.answer("📅 За сегодня пока нет записей.\nОтправьте мне свои мысли! ✨")
            return
            
        # Группируем записи по категориям
        categories = {}
        for text, category, datetime in entries:
            if category not in categories:
                categories[category] = []
            categories[category].append((text, datetime))
        
        # Формируем ответ
        response = "📅 <b>Записи за сегодня:</b>\n\n"
        
        for category, category_entries in categories.items():
            emoji = CATEGORY_EMOJIS.get(category, "📝")
            response += f"{emoji} <b>{category}</b> ({len(category_entries)}):\n"
            
            for text, datetime in category_entries:
                # Обрезаем длинный текст
                display_text = text[:100] + "..." if len(text) > 100 else text
                time_str = datetime.split()[1][:5] if ' ' in datetime else datetime
                response += f"• {display_text} <i>({time_str})</i>\n"
            
            response += "\n"
        
        # Если сообщение слишком длинное, разбиваем на части
        if len(response) > 4096:
            parts = [response[i:i+4096] for i in range(0, len(response), 4096)]
            for i, part in enumerate(parts):
                if i == 0:
                    await message.answer(part, parse_mode="HTML")
                else:
                    await message.answer(part, parse_mode="HTML")
        else:
            await message.answer(response, parse_mode="HTML")
            
        logger.info(f"Пользователю {user_id} показаны записи за сегодня ({len(entries)} записей)")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /сегодня: {e}")
        await message.answer("Произошла ошибка при получении записей. Попробуйте позже.") 