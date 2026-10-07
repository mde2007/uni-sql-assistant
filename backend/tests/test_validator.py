import pytest
from app.validator import validate_sql, ValidationError

GOOD = [
    "SELECT name FROM programs",
    "SELECT p.name, count(*) FROM v_applications AS a "
    "JOIN programs AS p ON p.id = a.program_id GROUP BY p.name",
    "SELECT avg(grade) FROM v_grades",
    "WITH t AS (SELECT program_id FROM v_students) SELECT count(*) FROM t",
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
    "SELECT student_code, grade FROM v_grades",
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
    "SELECT name FROM secret.programs",
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
