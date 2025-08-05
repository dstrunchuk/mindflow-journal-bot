"""
Модуль для парсинга времени из текста и создания напоминаний
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Паттерны для поиска времени
TIME_PATTERNS = [
    # "через X минут/часов/дней"
    (r'через\s+(\d+)\s+(минут|минуты|час|часа|часов|день|дня|дней)', 'relative'),
    # "в X:XX" или "в X часов"
    (r'в\s+(\d{1,2}):(\d{2})', 'time'),
    (r'в\s+(\d{1,2})\s+(час|часа|часов)', 'time_hours'),
    # "завтра в X:XX"
    (r'завтра\s+в\s+(\d{1,2}):(\d{2})', 'tomorrow_time'),
    # "через час", "через 2 часа"
    (r'через\s+(час|(\d+)\s+часа?)', 'relative_hours'),
    # "через полчаса", "через 30 минут"
    (r'через\s+(полчаса|30\s+минут)', 'half_hour'),
    # "23 августа", "15 сентября" и т.д.
    (r'(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)', 'date'),
    # "23 августа день рождения", "15 сентября встреча"
    (r'(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+(.*)', 'date_with_event'),
]


class ReminderParser:
    def __init__(self):
        self.patterns = TIME_PATTERNS

    def parse_time_from_text(self, text: str) -> Optional[Tuple[str, str]]:
        """
        Извлекает время из текста
        
        Args:
            text: Текст для анализа
            
        Returns:
            Tuple[str, str]: (время_напоминания, описание) или None
        """
        text_lower = text.lower()
        
        for pattern, pattern_type in self.patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    reminder_time = self._calculate_time(match, pattern_type)
                    if reminder_time:
                        description = self._create_description(match, pattern_type)
                        return reminder_time, description
                except Exception as e:
                    logger.error(f"Ошибка парсинга времени: {e}")
                    continue
        
        return None

    def _calculate_time(self, match, pattern_type: str) -> Optional[str]:
        """Вычисляет время напоминания"""
        now = datetime.now()
        
        if pattern_type == 'relative':
            amount = int(match.group(1))
            unit = match.group(2)
            
            if unit in ['минут', 'минуты']:
                reminder_time = now + timedelta(minutes=amount)
            elif unit in ['час', 'часа', 'часов']:
                reminder_time = now + timedelta(hours=amount)
            elif unit in ['день', 'дня', 'дней']:
                reminder_time = now + timedelta(days=amount)
            else:
                return None
                
        elif pattern_type == 'time':
            hour = int(match.group(1))
            minute = int(match.group(2))
            reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Если время уже прошло сегодня, переносим на завтра
            if reminder_time <= now:
                reminder_time += timedelta(days=1)
                
        elif pattern_type == 'time_hours':
            hour = int(match.group(1))
            reminder_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            # Если время уже прошло сегодня, переносим на завтра
            if reminder_time <= now:
                reminder_time += timedelta(days=1)
                
        elif pattern_type == 'tomorrow_time':
            hour = int(match.group(1))
            minute = int(match.group(2))
            tomorrow = now + timedelta(days=1)
            reminder_time = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
        elif pattern_type == 'relative_hours':
            if match.group(1) == 'час':
                amount = 1
            else:
                amount = int(match.group(2))
            reminder_time = now + timedelta(hours=amount)
            
        elif pattern_type == 'half_hour':
            reminder_time = now + timedelta(minutes=30)
            
        elif pattern_type == 'date':
            day = int(match.group(1))
            month_name = match.group(2)
            month_dict = {
                'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
                'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
            }
            month = month_dict[month_name]
            reminder_time = datetime(now.year, month, day, 0, 0, 0)
            
            # Если дата уже прошла в текущем году, переносим на следующий год
            if reminder_time <= now:
                reminder_time = datetime(now.year + 1, month, day, 0, 0, 0)
                
        elif pattern_type == 'date_with_event':
            day = int(match.group(1))
            month_name = match.group(2)
            month_dict = {
                'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
                'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
            }
            month = month_dict[month_name]
            event_name = match.group(3)
            reminder_time = datetime(now.year, month, day, 0, 0, 0)
            
            # Если дата уже прошла в текущем году, переносим на следующий год
            if reminder_time <= now:
                reminder_time = datetime(now.year + 1, month, day, 0, 0, 0)
                
        else:
            return None
            
        return reminder_time.strftime('%Y-%m-%d %H:%M:%S')

    def _create_description(self, match, pattern_type: str) -> str:
        """Создает описание напоминания"""
        if pattern_type == 'relative':
            amount = match.group(1)
            unit = match.group(2)
            return f"через {amount} {unit}"
        elif pattern_type == 'time':
            hour = match.group(1)
            minute = match.group(2)
            return f"в {hour}:{minute}"
        elif pattern_type == 'time_hours':
            hour = match.group(1)
            return f"в {hour}:00"
        elif pattern_type == 'tomorrow_time':
            hour = match.group(1)
            minute = match.group(2)
            return f"завтра в {hour}:{minute}"
        elif pattern_type == 'relative_hours':
            if match.group(1) == 'час':
                return "через час"
            else:
                amount = match.group(2)
                return f"через {amount} часа"
        elif pattern_type == 'half_hour':
            return "через полчаса"
        elif pattern_type == 'date':
            day = match.group(1)
            month_name = match.group(2)
            return f"{day} {month_name}"
        elif pattern_type == 'date_with_event':
            day = match.group(1)
            month_name = match.group(2)
            event_name = match.group(3)
            return f"{day} {month_name} {event_name}"
        else:
            return "напоминание"

    def should_create_reminder(self, text: str, category: str) -> bool:
        """Определяет, нужно ли создавать напоминание"""
        # Проверяем наличие временных указаний в любом тексте
        has_time = self.parse_time_from_text(text) is not None
        
        # Создаем напоминания для всех категорий, если есть временные указания
        if has_time:
            logger.info(f"Создание напоминания для категории '{category}' с временным указанием")
            return True
            
        return False 