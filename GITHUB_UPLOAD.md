# Загрузка на GitHub

## Шаги для загрузки проекта на GitHub:

### 1. Создайте репозиторий на GitHub
1. Перейдите на https://github.com
2. Нажмите "New" или "+" → "New repository"
3. Название: `mindflow-journal-bot`
4. Описание: `Telegram bot for thought journaling with automatic categorization`
5. Выберите Public или Private
6. **НЕ** ставьте галочки на:
   - ✅ Add a README file
   - ✅ Add .gitignore  
   - ✅ Choose a license
7. Нажмите "Create repository"

### 2. Подключите локальный репозиторий к GitHub
```bash
# Замените YOUR_USERNAME на ваше имя пользователя GitHub
git remote add origin https://github.com/YOUR_USERNAME/mindflow-journal-bot.git
git branch -M main
git push -u origin main
```

### 3. Альтернативный способ (если у вас есть GitHub CLI)
```bash
# Создание репозитория через GitHub CLI
gh repo create mindflow-journal-bot --public --description "Telegram bot for thought journaling with automatic categorization" --source=. --remote=origin --push
```

### 4. Проверка загрузки
После успешной загрузки перейдите на:
`https://github.com/YOUR_USERNAME/mindflow-journal-bot`

## Структура проекта на GitHub:
```
mindflow-journal-bot/
├── README.md              # Основная документация
├── INSTALL.md             # Быстрая установка
├── requirements.txt       # Зависимости Python
├── main.py               # Главный файл бота
├── config.py             # Конфигурация
├── env_example.txt       # Пример настройки токена
├── .gitignore           # Исключения Git
├── db/                  # Модули базы данных
├── handlers/            # Обработчики команд
└── utils/               # Утилиты
```

## После загрузки:
1. Добавьте описание проекта в README
2. Настройте теги (Topics): `telegram-bot`, `python`, `aiogram`, `journal`, `categorization`
3. Добавьте лицензию если нужно
4. Настройте GitHub Pages для документации (опционально)

## Полезные команды для дальнейшей работы:
```bash
# Добавить изменения
git add .
git commit -m "Описание изменений"
git push

# Создать новую ветку
git checkout -b feature/new-feature
git push -u origin feature/new-feature

# Обновить локальный репозиторий
git pull origin main
``` 