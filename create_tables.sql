-- Создание таблицы записей
CREATE TABLE IF NOT EXISTS entries (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category TEXT NOT NULL
);

-- Создание индекса для записей
CREATE INDEX IF NOT EXISTS idx_entries_user_datetime ON entries(user_id, datetime);

-- Создание таблицы пользовательских категорий
CREATE TABLE IF NOT EXISTS custom_categories (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name TEXT NOT NULL,
    keywords TEXT NOT NULL,
    UNIQUE(user_id, name)
);

-- Создание таблицы напоминаний
CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    entry_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    reminder_time TIMESTAMP NOT NULL,
    is_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индекса для напоминаний
CREATE INDEX IF NOT EXISTS idx_reminders_user_time ON reminders(user_id, reminder_time);

-- Проверка создания таблиц
SELECT 'entries' as table_name, COUNT(*) as row_count FROM entries
UNION ALL
SELECT 'custom_categories' as table_name, COUNT(*) as row_count FROM custom_categories
UNION ALL
SELECT 'reminders' as table_name, COUNT(*) as row_count FROM reminders; 