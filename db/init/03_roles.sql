-- Роль создаётся, только если её ещё нет.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'assistant_ro') THEN
        CREATE ROLE assistant_ro LOGIN PASSWORD 'ro_password' CONNECTION LIMIT 50;
    END IF;
END
$$;

GRANT CONNECT ON DATABASE university TO assistant_ro;
GRANT USAGE ON SCHEMA public TO assistant_ro;

-- Только представления и справочники.
GRANT SELECT ON v_applications, v_students, v_grades, v_teachers,
                faculties, departments, programs, disciplines
TO assistant_ro;

-- если валидатор что-то пропустит, то бд сама не даст писать и зависать
ALTER ROLE assistant_ro SET default_transaction_read_only = on;
ALTER ROLE assistant_ro SET statement_timeout = '5s';
ALTER ROLE assistant_ro SET idle_in_transaction_session_timeout = '10s';