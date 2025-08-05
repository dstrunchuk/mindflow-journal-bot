"""
MindFlow Journal - Telegram бот для ведения дневника мыслей
"""

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.utils.i18n import I18nMiddleware

# Импорты конфигурации и компонентов
import config
from db.database import Database
from db.postgres_database import PostgresDatabase
from db.supabase_database import SupabaseDatabase
from utils.categorizer import Categorizer

# Импорты обработчиков
from handlers.start import router as start_router
from handlers.dump import router as dump_router
from handlers.today import router as today_router
from handlers.search import router as search_router
from handlers.categories import router as categories_router
from handlers.archive import router as archive_router, state_router as archive_state_router
from handlers.add_category import router as add_category_router
from handlers.reminders import router as reminders_router

# Импорты утилит
from utils.reminder_scheduler import ReminderScheduler

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler('mindflow_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="today", description="Записи за сегодня"),
        BotCommand(command="search", description="Поиск по записям"),
        BotCommand(command="categories", description="Все категории"),
        BotCommand(command="addcategory", description="Добавить свою категорию"),
        BotCommand(command="archive", description="Записи за конкретную дату"),
        BotCommand(command="reminders", description="Мои напоминания"),
    ]
    await bot.set_my_commands(commands)


async def main():
    """Главная функция запуска бота"""
    try:
        logger.info("Запуск MindFlow Journal бота...")
        
        # Инициализация бота и диспетчера
        bot = Bot(token=config.BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        
        # Инициализация базы данных
        if config.SUPABASE_KEY and config.SUPABASE_KEY.strip():
            database = SupabaseDatabase(config.SUPABASE_URL, config.SUPABASE_KEY)
            logger.info("Используется Supabase API")
        elif config.DATABASE_URL and config.DATABASE_URL.strip():
            database = PostgresDatabase(config.DATABASE_URL)
            logger.info("Используется PostgreSQL база данных")
        else:
            database = Database(config.DATABASE_PATH)
            logger.info("Используется SQLite база данных (fallback)")
        
        await database.connect()
        logger.info("База данных подключена")
        
        # Инициализация категоризатора
        categorizer = Categorizer(database)
        logger.info("Категоризатор инициализирован")
        
        # Внедрение зависимостей через middleware
        from aiogram.fsm.middleware import BaseMiddleware
        
        class DependencyMiddleware(BaseMiddleware):
            def __init__(self, database, categorizer):
                super().__init__()
                self.database = database
                self.categorizer = categorizer
            
            async def __call__(self, handler, event, data):
                logger.info(f"=== MIDDLEWARE СРАБОТАЛ ===")
                logger.info(f"Тип события: {type(event)}")
                if hasattr(event, 'text'):
                    logger.info(f"Текст события: '{event.text}'")
                data["database"] = self.database
                data["categorizer"] = self.categorizer
                logger.info("Зависимости добавлены в data")
                return await handler(event, data)
        
        # Применяем middleware ко всем роутерам
        middleware = DependencyMiddleware(database, categorizer)
        dp.message.middleware(middleware)
        dp.callback_query.middleware(middleware)
        
        # Регистрация роутеров
        dp.include_router(start_router)
        dp.include_router(today_router)
        dp.include_router(search_router)
        dp.include_router(categories_router)
        dp.include_router(archive_router)
        dp.include_router(archive_state_router)  # Роутер для состояний архива
        dp.include_router(add_category_router)
        dp.include_router(reminders_router)
        dp.include_router(dump_router)  # Должен быть последним для обработки текста
        
        # Установка команд бота
        await set_commands(bot)
        logger.info("Команды бота установлены")
        
        # Запуск планировщика напоминаний
        scheduler = ReminderScheduler(bot, database)
        asyncio.create_task(scheduler.start())
        logger.info("Планировщик напоминаний запущен")
        
        logger.info("MindFlow Journal бот запущен и готов к работе!")
        
        # Запуск бота
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
        raise
    finally:
        # Закрытие соединений
        if 'database' in locals():
            await database.disconnect()
        if 'bot' in locals():
            await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        sys.exit(1) 