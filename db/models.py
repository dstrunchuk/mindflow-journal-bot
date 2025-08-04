"""
Модели базы данных для MindFlow Journal
"""

# SQL-запросы для создания таблиц
CREATE_ENTRIES_TABLE = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category TEXT NOT NULL
)
"""

CREATE_ENTRIES_INDEX = """
CREATE INDEX IF NOT EXISTS idx_entries_user_datetime ON entries(user_id, datetime)
"""

CREATE_CUSTOM_CATEGORIES_TABLE = """
CREATE TABLE IF NOT EXISTS custom_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    keywords TEXT NOT NULL,
    UNIQUE(user_id, name)
)
"""

CREATE_REMINDERS_TABLE = """
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    entry_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    reminder_time TIMESTAMP NOT NULL,
    is_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE
)
"""

CREATE_REMINDERS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_reminders_user_time ON reminders(user_id, reminder_time)
"""

# SQL-запросы для работы с записями
INSERT_ENTRY = """
INSERT INTO entries (user_id, text, category) VALUES (?, ?, ?)
"""

GET_TODAY_ENTRIES = """
SELECT text, category, datetime 
FROM entries 
WHERE user_id = ? AND DATE(datetime) = DATE('now', 'localtime')
ORDER BY datetime DESC
"""

GET_ENTRIES_BY_DATE = """
SELECT text, category, datetime 
FROM entries 
WHERE user_id = ? AND DATE(datetime) = ?
ORDER BY datetime DESC
"""

SEARCH_ENTRIES = """
SELECT text, category, datetime 
FROM entries 
WHERE user_id = ? AND text LIKE ?
ORDER BY datetime DESC
"""

# SQL-запросы для работы с пользовательскими категориями
INSERT_CUSTOM_CATEGORY = """
INSERT OR REPLACE INTO custom_categories (user_id, name, keywords) VALUES (?, ?, ?)
"""

GET_CUSTOM_CATEGORIES = """
SELECT name, keywords FROM custom_categories WHERE user_id = ?
"""

GET_ALL_CUSTOM_CATEGORIES = """
SELECT user_id, name, keywords FROM custom_categories
"""

# SQL-запросы для работы с напоминаниями
INSERT_REMINDER = """
INSERT INTO reminders (user_id, entry_id, text, reminder_time) VALUES (?, ?, ?, ?)
"""

GET_PENDING_REMINDERS = """
SELECT id, user_id, text, reminder_time 
FROM reminders 
WHERE reminder_time <= datetime('now', 'localtime') AND is_sent = FALSE
ORDER BY reminder_time ASC
"""

MARK_REMINDER_SENT = """
UPDATE reminders SET is_sent = TRUE WHERE id = ?
"""

GET_USER_REMINDERS = """
SELECT id, text, reminder_time, is_sent 
FROM reminders 
WHERE user_id = ? 
ORDER BY reminder_time DESC
""" 