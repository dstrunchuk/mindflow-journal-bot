"""
Обработчик для сохранения текстовых сообщений
"""

import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text & ~F.text.startswith('/'))
async def handle_text_message(message: Message, database, categorizer):
    """Обработчик текстовых сообщений - сохранение мыслей"""
    try:
        user_id = message.from_user.id
        text = message.text.strip()
        
        if not text:
            await message.answer("Пожалуйста, отправьте непустое сообщение.")
            return
            
        # Категоризируем текст
        category, emoji = await categorizer.categorize(text, user_id)
        
        # Сохраняем в базу данных
        success = await database.add_entry(user_id, text, category)
        
        if success:
            response = f"✅ Записано!\nКатегория: {emoji} {category}"
            await message.answer(response)
            logger.info(f"Сообщение пользователя {user_id} сохранено в категорию '{category}'")
        else:
            await message.answer("❌ Ошибка при сохранении. Попробуйте позже.")
            logger.error(f"Ошибка сохранения сообщения пользователя {user_id}")
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике текстовых сообщений: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.") 