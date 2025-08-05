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
SUPABASE_KEY = os.getenv('SUPABASE_KEY')  # Читаем из переменных окружения

# Настройки базы данных
DATABASE_URL = os.getenv('DATABASE_URL')  # Читаем из переменных окружения
DATABASE_PATH = "mindflow.db"  # Используем SQLite как fallback

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 