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

logger.info("=== РОУТЕР DUMP ЗАГРУЖЕН ===")
logger.info(f"Роутер: {router}")
logger.info(f"Обработчики в роутере: {len(router.message.handlers)}")


@router.message()
async def handle_all_messages(message: Message):
    """Обработчик всех сообщений для отладки"""
    logger.info(f"=== ПОЛУЧЕНО СООБЩЕНИЕ ===")
    logger.info(f"Тип: {message.content_type}")
    logger.info(f"Текст: '{message.text}'")
    logger.info(f"От пользователя: {message.from_user.id}")
    
    # Если это команда, не обрабатываем
    if message.text and message.text.startswith('/'):
        logger.info("Это команда, пропускаем")
        return
    
    # Если это не текст, отвечаем
    if message.content_type != "text":
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return


@router.message(F.text & ~F.text.startswith('/'))
async def handle_text_message(message: Message, database, categorizer):
    """Обработчик текстовых сообщений - сохранение мыслей"""
    try:
        logger.info(f"=== ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ АКТИВИРОВАН ===")
        logger.info(f"Тип сообщения: {message.content_type}")
        logger.info(f"Текст сообщения: '{message.text}'")
        logger.info(f"Начинается с '/': {message.text.startswith('/') if message.text else 'None'}")
        
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
        logger.error(f"Тип ошибки: {type(e)}")
        await message.answer("Произошла ошибка. Попробуйте позже.") 