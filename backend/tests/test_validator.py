import pytest
from app.validator import validate_sql, ValidationError

GOOD = [
    "SELECT f.name, round(avg(g.grade), 2) FROM v_grades AS g "
    "JOIN programs AS p ON p.id = g.program_id JOIN faculties AS f ON f.id = p.faculty_id GROUP BY f.name",
    "SELECT name FROM api.programs",
    "SELECT name FROM programs",
    "SELECT p.name, count(*) FROM v_applications AS a "
    "JOIN programs AS p ON p.id = a.program_id GROUP BY p.name",
    "SELECT avg(grade) FROM v_grades",
    "WITH t AS (SELECT program_id FROM v_students) SELECT count(*) FROM t",
    # обычные функции из белого списка
    "SELECT EXTRACT(YEAR FROM submitted_at) AS y, count(*) FROM v_applications GROUP BY y",
    "SELECT string_agg(name, ', ') FROM programs",
    "SELECT CASE WHEN grade >= 4 THEN 'хорошо' ELSE 'плохо' END AS g, count(*) FROM v_grades GROUP BY 1",
    "SELECT coalesce(round(avg(exam_score), 1), 0) FROM v_applications WHERE year = 2026 OR year = 2025",
    # ORDER BY по псевдониму, совпадающему с именем таблицы
    "SELECT f.name, count(*) AS programs FROM programs AS p "
    "JOIN faculties AS f ON f.id = p.faculty_id GROUP BY f.name ORDER BY programs DESC",
]

BAD = [
    "DROP TABLE students",
    "DELETE FROM programs",
    "UPDATE programs SET name = 'x'",
    "INSERT INTO programs (name) VALUES ('x')",
    "SELECT * FROM students",
    "SELECT passport FROM applicants",
    "SELECT 1; DROP TABLE programs",
    "SELECT pg_sleep(10)",
    "SELECT * FROM v_students",
    "SELECT table_name FROM information_schema.tables",
    "WITH x AS (DELETE FROM programs RETURNING id) SELECT id FROM x",
    "SELECT name FROM programs UNION SELECT passport FROM applicants",
    # новые атаки (Шаг 4.4)
    "dElEtE FROM programs",
    "SELECT usename FROM pg_catalog.pg_user",
    "SELECT name FROM programs WHERE id IN (SELECT id FROM students)",
    "SELECT name FROM programs /* x */; DROP TABLE programs",
    "SELECT pg_read_file('/etc/passwd')",
    "SELECT set_config('statement_timeout', '0', false)",
    "SELECT name INTO newtable FROM programs",
    "",
    "это не SQL вообще",
    "SELECT name FROM public.students",
    "SELECT name FROM public.programs",
    "SELECT name FROM secret.programs",
    # ссылки на всю строку таблицы: вытаскивают все столбцы сразу
    "SELECT g FROM v_grades AS g",
    "SELECT row_to_json(g) FROM v_grades AS g",
    "SELECT json_agg(g) FROM v_grades AS g",
    "SELECT (g).grade FROM v_grades AS g",
    "SELECT to_jsonb(v_grades) FROM v_grades",
    "SELECT count(*) FROM v_grades AS g WHERE g::text LIKE '%a%'",
    "WITH t AS (SELECT grade FROM v_grades) SELECT array_agg(t) FROM t",
    # функции не из белого списка, в том числе исполняющие SQL из строки
    "SELECT query_to_xml_and_xmlschema('select full_name from students', true, false, '')",
    "SELECT table_to_xml('v_grades', true, false, '')",
    "SELECT cursor_to_xml('c', 10, true, false, '')",
    "SELECT version()",
    "SELECT pg_catalog.pg_sleep(10)",
]


@pytest.mark.parametrize("sql", GOOD)
def test_good_queries_pass(sql):
    result = validate_sql(sql)
    assert "LIMIT" in result.upper()


@pytest.mark.parametrize("sql", BAD)
def test_bad_queries_rejected(sql):
    with pytest.raises(ValidationError):
        validate_sql(sql)


def test_big_limit_is_reduced():
    result = validate_sql("SELECT name FROM programs LIMIT 1000000")
    assert "LIMIT 1000" in result
    assert "1000000" not in result


def test_small_limit_is_kept():
    result = validate_sql("SELECT name FROM programs LIMIT 5")
    assert "LIMIT 5" in result


def test_limit_all_becomes_limit_1000():
    result = validate_sql("SELECT name FROM programs LIMIT ALL")
    assert "LIMIT 1000" in result
    assert "ALL" not in result.upper().replace("LIMIT 1000", "")
