"""
Обработчик для сохранения текстовых сообщений
"""

import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.reminder_parser import ReminderParser

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text & ~F.text.startswith('/'))
async def handle_text_message(message: Message, database, categorizer):
    """Обработчик текстовых сообщений - сохранение мыслей"""
    try:
        user_id = message.from_user.id
        text = message.text.strip()
        
        logger.info(f"Получено текстовое сообщение от пользователя {user_id}: '{text}'")
        
        if not text:
            await message.answer("Пожалуйста, отправьте непустое сообщение.")
            return
            
        # Категоризируем текст
        category, emoji = await categorizer.categorize(text, user_id)
        logger.info(f"Текст категоризирован как '{category}' с эмодзи '{emoji}'")
        
        # Сохраняем в базу данных
        logger.info(f"Попытка сохранения записи в базу данных...")
        entry_id = await database.add_entry(user_id, text, category)
        logger.info(f"Результат сохранения записи, получен ID: {entry_id}")
        
        if entry_id:
            response = f"✅ Записано!\nКатегория: {emoji} {category}"
            
            # Проверяем, нужно ли создать напоминание
            reminder_parser = ReminderParser()
            should_create = reminder_parser.should_create_reminder(text, category)
            logger.info(f"Проверка напоминания: категория='{category}', should_create={should_create}")
            
            if should_create:
                reminder_data = reminder_parser.parse_time_from_text(text)
                if reminder_data:
                    reminder_time, description = reminder_data
                    logger.info(f"Создание напоминания: время='{reminder_time}', описание='{description}'")
                    success = await database.add_reminder(user_id, entry_id, text, reminder_time)
                    if success:
                        response += f"\n⏰ Напоминание создано: {description}"
                        logger.info(f"Напоминание создано для пользователя {user_id} на {reminder_time}")
                    else:
                        response += "\n⚠️ Ошибка создания напоминания"
                        logger.error(f"Ошибка создания напоминания для пользователя {user_id}")
                else:
                    logger.info("Время не найдено в тексте для напоминания")
            
            await message.answer(response)
            logger.info(f"Сообщение пользователя {user_id} сохранено в категорию '{category}'")
        else:
            await message.answer("❌ Ошибка при сохранении. Попробуйте позже.")
            logger.error(f"Ошибка сохранения сообщения пользователя {user_id}")
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике текстовых сообщений: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.") 