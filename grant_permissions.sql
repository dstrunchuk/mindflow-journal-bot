-- Отключение Row Level Security для всех таблиц
ALTER TABLE entries DISABLE ROW LEVEL SECURITY;
ALTER TABLE custom_categories DISABLE ROW LEVEL SECURITY;
ALTER TABLE reminders DISABLE ROW LEVEL SECURITY;

-- Предоставление всех прав для анонимных пользователей
GRANT ALL ON entries TO anon;
GRANT ALL ON custom_categories TO anon;
GRANT ALL ON reminders TO anon;

-- Предоставление прав на использование последовательностей (для SERIAL полей)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;

-- Предоставление прав на схему public
GRANT ALL ON SCHEMA public TO anon;

-- Проверка текущих прав (исправленная версия)
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename IN ('entries', 'custom_categories', 'reminders');

-- Проверка прав пользователя anon
SELECT 
    grantee,
    table_name,
    privilege_type
FROM information_schema.role_table_grants 
WHERE grantee = 'anon' 
AND table_name IN ('entries', 'custom_categories', 'reminders'); 