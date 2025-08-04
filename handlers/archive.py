"""
Обработчик команды /архив
"""

import logging
import re
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.categorizer import CATEGORY_EMOJIS

logger = logging.getLogger(__name__)
router = Router()

# Состояния для ожидания даты
user_states = {}


@router.message(Command("archive"))
async def cmd_archive(message: Message):
    """Обработчик команды /archive - запрос даты"""
    try:
        user_id = message.from_user.id
        user_states[user_id] = "waiting_date"
        
        response = """📅 <b>Архив записей</b>

Отправьте дату в формате ГГГГ-ММ-ДД

Примеры:
• 2024-01-15
• 2024-12-31

Или отправьте 'сегодня' для просмотра записей за сегодня."""
        
        await message.answer(response, parse_mode="HTML")
        logger.info(f"Пользователь {user_id} запросил архив")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /архив: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


# Создаем отдельный роутер для обработки состояний
state_router = Router()


@state_router.message(F.text & ~F.text.startswith('/'))
async def handle_date_input(message: Message, database):
    """Обработчик ввода даты для архива"""
    try:
        user_id = message.from_user.id
        
        # Проверяем, ожидаем ли мы дату от этого пользователя
        if user_id not in user_states or user_states[user_id] != "waiting_date":
            return
            
        # Убираем состояние ожидания
        del user_states[user_id]
        
        date_input = message.text.strip().lower()
        
        # Обработка специальных случаев
        if date_input == "сегодня":
            target_date = datetime.now().strftime("%Y-%m-%d")
        else:
            # Проверяем формат даты
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_input):
                await message.answer("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД\n\nПример: 2024-01-15")
                return
                
            # Проверяем корректность даты
            try:
                datetime.strptime(date_input, "%Y-%m-%d")
                target_date = date_input
            except ValueError:
                await message.answer("❌ Неверная дата. Проверьте правильность введенной даты.")
                return
        
        # Получаем записи за указанную дату
        entries = await database.get_entries_by_date(user_id, target_date)
        
        if not entries:
            await message.answer(f"📅 За {target_date} записей не найдено.")
            return
            
        # Группируем записи по категориям
        categories = {}
        for text, category, datetime_str in entries:
            if category not in categories:
                categories[category] = []
            categories[category].append((text, datetime_str))
        
        # Формируем ответ
        response = f"📅 <b>Записи за {target_date}:</b>\n\n"
        
        for category, category_entries in categories.items():
            emoji = CATEGORY_EMOJIS.get(category, "📝")
            response += f"{emoji} <b>{category}</b> ({len(category_entries)}):\n"
            
            for text, datetime_str in category_entries:
                # Обрезаем длинный текст
                display_text = text[:100] + "..." if len(text) > 100 else text
                time_str = datetime_str.split()[1][:5] if ' ' in datetime_str else datetime_str
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
            
        logger.info(f"Пользователю {user_id} показаны записи за {target_date} ({len(entries)} записей)")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике ввода даты: {e}")
        await message.answer("Произошла ошибка при получении записей. Попробуйте позже.") 