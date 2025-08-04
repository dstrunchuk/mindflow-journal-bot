"""
Обработчик команды /categories
"""

import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.categorizer import CATEGORIES, CATEGORY_EMOJIS

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("categories"))
async def cmd_categories(message: Message, database):
    """Обработчик команды /categories - показать все категории"""
    try:
        user_id = message.from_user.id
        
        # Получаем системные категории
        response = "📂 <b>Системные категории:</b>\n\n"
        
        for category_name, keywords in CATEGORIES.items():
            if category_name == "Прочее":
                continue  # Пропускаем "Прочее"
                
            emoji = CATEGORY_EMOJIS.get(category_name, "📝")
            keywords_str = ", ".join(keywords[:5])  # Показываем первые 5 ключевых слов
            if len(keywords) > 5:
                keywords_str += "..."
                
            response += f"{emoji} <b>{category_name}</b>\n"
            response += f"   Ключевые слова: {keywords_str}\n\n"
        
        # Получаем пользовательские категории
        custom_categories = await database.get_custom_categories(user_id)
        
        if custom_categories:
            response += "🔧 <b>Ваши категории:</b>\n\n"
            
            for name, keywords in custom_categories:
                keywords_list = [kw.strip() for kw in keywords.split(',')]
                keywords_str = ", ".join(keywords_list[:5])
                if len(keywords_list) > 5:
                    keywords_str += "..."
                    
                response += f"🔧 <b>{name}</b>\n"
                response += f"   Ключевые слова: {keywords_str}\n\n"
        else:
            response += "🔧 <b>Ваши категории:</b>\n"
            response += "   Пока нет пользовательских категорий\n\n"
        
        response += "💡 <b>Как добавить свою категорию:</b>\n"
        response += "/addcategory Название:ключ1,ключ2,ключ3\n\n"
        response += "Пример: /addcategory Работа:проект,задача,дедлайн"
        
        await message.answer(response, parse_mode="HTML")
        logger.info(f"Пользователю {user_id} показаны категории")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /категории: {e}")
        await message.answer("Произошла ошибка при получении категорий. Попробуйте позже.") 