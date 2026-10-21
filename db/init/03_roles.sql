DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'university_assistant') THEN
        CREATE ROLE university_assistant LOGIN PASSWORD 'ro_password' CONNECTION LIMIT 50;
    END IF;
END
$$;

GRANT CONNECT ON DATABASE university TO university_assistant;

-- В public (там таблицы с личными данными) ассистент даже не может заглянуть.
REVOKE ALL ON SCHEMA public FROM PUBLIC;
-- права из старой версии скрипта (справочники лежали в public)
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM university_assistant;

REVOKE ALL ON SCHEMA public FROM university_assistant;

GRANT USAGE ON SCHEMA api TO university_assistant;

GRANT SELECT ON ALL TABLES IN SCHEMA api TO university_assistant;

ALTER ROLE university_assistant SET search_path = api;

-- Функции, которые выполняют SQL из строки (в обход валидатора) или подвешивают базу.
DO $$
DECLARE
    func regprocedure;
BEGIN
    FOR func IN
        SELECT p.oid::regprocedure
        FROM pg_proc AS p
        JOIN pg_namespace AS n ON n.oid = p.pronamespace
        WHERE n.nspname = 'pg_catalog'
          AND (p.proname LIKE 'query\_to\_xml%'
              OR p.proname LIKE 'table\_to\_xml%'
              OR p.proname LIKE 'cursor\_to\_xml%'
              OR p.proname LIKE 'schema\_to\_xml%'
              OR p.proname LIKE 'database\_to\_xml%'
              OR p.proname LIKE 'pg\_sleep%')
    LOOP
        EXECUTE format('REVOKE EXECUTE ON FUNCTION %s FROM PUBLIC', func);
    END LOOP;
END
$$;

-- если валидатор что-то пропустит, то БД сама не даст писать и зависать
ALTER ROLE university_assistant
SET
    default_transaction_read_only = on;

ALTER ROLE university_assistant
SET
    statement_timeout = '5s';

ALTER ROLE university_assistant
SET
    idle_in_transaction_session_timeout = '10s';