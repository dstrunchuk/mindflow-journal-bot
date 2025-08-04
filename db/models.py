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