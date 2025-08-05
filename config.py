import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Конфигурация бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения. Создайте файл .env с BOT_TOKEN=ваш_токен")

# Настройки Supabase
SUPABASE_URL = "https://kdwiyhxjnucgpwbzcvz.supabase.co"
SUPABASE_KEY = None  # Временно отключаем Supabase из-за проблем с DNS

# Настройки базы данных
DATABASE_URL = None  # Не используем PostgreSQL connection string
DATABASE_PATH = "mindflow.db"  # Используем SQLite

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 