"""
Обработчик команды /добавитькатегорию
"""

import logging
import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("addcategory"))
async def cmd_add_category(message: Message, database, categorizer):
    """Обработчик команды /addcategory - добавление пользовательской категории"""
    try:
        user_id = message.from_user.id
        text = message.text.strip()
        
        # Извлекаем параметры команды
        if text.startswith('/addcategory'):
            params = text[12:].strip()  # Убираем '/addcategory ' из начала
            
        if not params:
            await message.answer("""🔧 <b>Добавление категории</b>

Использование: /addcategory Название:ключ1,ключ2,ключ3

Примеры:
• /addcategory Работа:проект,задача,дедлайн
• /addcategory Здоровье:спорт,диета,врач
• /addcategory Финансы:деньги,бюджет,траты""", parse_mode="HTML")
            return
            
        # Парсим название и ключевые слова
        if ':' not in params:
            await message.answer("❌ Неверный формат. Используйте: Название:ключ1,ключ2,ключ3")
            return
            
        name_part, keywords_part = params.split(':', 1)
        category_name = name_part.strip()
        keywords_str = keywords_part.strip()
        
        # Проверяем название категории
        if not category_name:
            await message.answer("❌ Название категории не может быть пустым")
            return
            
        if len(category_name) > 50:
            await message.answer("❌ Название категории слишком длинное (максимум 50 символов)")
            return
            
        # Проверяем ключевые слова
        if not keywords_str:
            await message.answer("❌ Ключевые слова не могут быть пустыми")
            return
            
        keywords_list = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
        
        if not keywords_list:
            await message.answer("❌ Не найдено валидных ключевых слов")
            return
            
        if len(keywords_list) > 20:
            await message.answer("❌ Слишком много ключевых слов (максимум 20)")
            return
            
        # Проверяем длину каждого ключевого слова
        for keyword in keywords_list:
            if len(keyword) > 30:
                await message.answer(f"❌ Ключевое слово '{keyword}' слишком длинное (максимум 30 символов)")
                return
                
        # Сохраняем категорию в базу данных
        success = await database.add_custom_category(user_id, category_name, keywords_str)
        
        if success:
            # Инвалидируем кэш категоризатора
            await categorizer.invalidate_cache()
            
            response = f"✅ Категория '{category_name}' успешно добавлена!\n\n"
            response += f"🔧 <b>{category_name}</b>\n"
            response += f"Ключевые слова: {', '.join(keywords_list)}"
            
            await message.answer(response, parse_mode="HTML")
            logger.info(f"Пользователь {user_id} добавил категорию '{category_name}' с ключевыми словами: {keywords_list}")
        else:
            await message.answer("❌ Ошибка при добавлении категории. Попробуйте позже.")
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике /добавитькатегорию: {e}")
        await message.answer("Произошла ошибка при добавлении категории. Попробуйте позже.") 