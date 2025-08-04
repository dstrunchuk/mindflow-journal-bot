"""
Обработчик команды /поиск
"""

import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.categorizer import CATEGORY_EMOJIS

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("search"))
async def cmd_search(message: Message, database):
    """Обработчик команды /search - поиск записей по ключевому слову"""
    try:
        user_id = message.from_user.id
        text = message.text.strip()
        
        # Извлекаем поисковый запрос
        if text.startswith('/search'):
            search_term = text[8:].strip()  # Убираем '/search ' из начала
            
        if not search_term:
            await message.answer("🔍 Использование: /search <слово>\n\nПример: /search проект")
            return
            
        # Ищем записи
        entries = await database.search_entries(user_id, search_term)
        
        if not entries:
            await message.answer(f"🔍 По запросу '{search_term}' ничего не найдено.")
            return
            
        # Формируем ответ
        response = f"🔍 <b>Результаты поиска по '{search_term}':</b>\n\n"
        
        for i, (text, category, datetime) in enumerate(entries[:20], 1):  # Ограничиваем 20 результатами
            emoji = CATEGORY_EMOJIS.get(category, "📝")
            # Обрезаем длинный текст
            display_text = text[:150] + "..." if len(text) > 150 else text
            date_str = datetime.split()[0] if ' ' in datetime else datetime
            time_str = datetime.split()[1][:5] if ' ' in datetime else ""
            
            response += f"{i}. {emoji} <b>{category}</b>\n"
            response += f"   {display_text}\n"
            response += f"   <i>{date_str} {time_str}</i>\n\n"
        
        if len(entries) > 20:
            response += f"... и ещё {len(entries) - 20} записей"
        
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
            
        logger.info(f"Пользователь {user_id} искал '{search_term}', найдено {len(entries)} записей")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /поиск: {e}")
        await message.answer("Произошла ошибка при поиске. Попробуйте позже.") 