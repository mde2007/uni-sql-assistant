-- Пользователь «только чтение» для ассистента.
-- Имена представлений уточни у Студента 2 и поправь список ниже.
CREATE ROLE assistant_ro LOGIN PASSWORD 'ro_password' CONNECTION LIMIT 50;
GRANT CONNECT ON DATABASE university TO assistant_ro;
GRANT USAGE ON SCHEMA public TO assistant_ro;

-- Только представления и справочники.
-- Таблиц students, applicants, grades, applications, teachers здесь НЕТ.
GRANT SELECT ON v_applications, v_students, v_grades, v_teachers,
                faculties, programs, disciplines
TO assistant_ro;

-- Даже если валидатор что-то пропустит, база сама не даст писать и зависать
ALTER ROLE assistant_ro SET default_transaction_read_only = on;
ALTER ROLE assistant_ro SET statement_timeout = '5s';
ALTER ROLE assistant_ro SET idle_in_transaction_session_timeout = '10s';
