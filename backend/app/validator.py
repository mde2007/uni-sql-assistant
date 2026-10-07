import sqlglot
from sqlglot import exp

try:
    from app.config import MAX_ROWS
except Exception:  # на случай, если у Студента 1 константа названа иначе
    MAX_ROWS = 1000

ALLOWED_TABLES = {
    "v_applications", "v_students", "v_grades", "v_teachers",
    "faculties", "programs", "disciplines",
}

FORBIDDEN_FUNCTIONS = {
    "pg_sleep", "pg_sleep_for", "pg_sleep_until", "pg_read_file",
    "pg_read_binary_file", "pg_ls_dir", "dblink", "lo_import", "lo_export",
    "set_config", "pg_terminate_backend", "pg_cancel_backend",
    "pg_advisory_lock", "query_to_xml", "current_setting",
}


class ValidationError(Exception):
    pass


def validate_sql(sql):
    """Возвращает безопасный SQL с LIMIT или бросает ValidationError."""
    sql = (sql or "").strip().rstrip(";").strip()
    if not sql:
        raise ValidationError("пустой запрос")

    # 1. Разбираем SQL в дерево
    try:
        statements = sqlglot.parse(sql, read="postgres")
    except sqlglot.errors.SqlglotError:
        raise ValidationError("не удалось разобрать SQL")

    # 2. Ровно один запрос
    if len(statements) != 1 or statements[0] is None:
        raise ValidationError("разрешён ровно один запрос")
    tree = statements[0]

    # 3. Только SELECT (или UNION/INTERSECT/EXCEPT из SELECT)
    if not isinstance(tree, (exp.Select, exp.Union)):
        raise ValidationError("разрешены только запросы SELECT")

    # 4. Внутри не должно быть изменяющих команд (например, в WITH)
    if tree.find(exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create,
                 exp.Command, exp.Into) is not None:
        raise ValidationError("запрещённая команда внутри запроса")

    # 5. Только таблицы из белого списка
    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    for table in tree.find_all(exp.Table):
        name = table.name.lower()
        if not table.db and name in cte_names:
            continue  # временная таблица из WITH
        if table.db and table.db.lower() != "public":
            raise ValidationError(f"схема {table.db} запрещена")
        if name not in ALLOWED_TABLES:
            raise ValidationError(f"таблица {name} запрещена")

    # 6. Опасные функции (и вызванные как Anonymous, и как известные sqlglot)
    for func in tree.find_all(exp.Func):
        fname = (func.name if isinstance(func, exp.Anonymous) else func.sql_name()).lower()
        if fname in FORBIDDEN_FUNCTIONS:
            raise ValidationError(f"функция {fname} запрещена")

    # 7. Персональные данные: проверяем ВСЕ SELECT, включая подзапросы и WITH
    for sel in tree.find_all(exp.Select):
        for column in sel.expressions:
            has_aggregate = column.find(exp.AggFunc) is not None
            if column.find(exp.Star) is not None and not has_aggregate:
                raise ValidationError("SELECT * запрещён, нужно перечислить столбцы")
            for col in column.find_all(exp.Column):
                if col.name.lower() == "student_code" and col.find_ancestor(exp.Count) is None:
                    raise ValidationError("код студента можно использовать только внутри count()")

    # 8. LIMIT: ставим, если нет, или уменьшаем, если слишком большой
    if isinstance(tree, exp.Union):
        return f"SELECT * FROM ({tree.sql(dialect='postgres')}) AS u LIMIT {MAX_ROWS}"

    limit = tree.args.get("limit")
    if limit is None:
        tree = tree.limit(MAX_ROWS)
    else:
        value = limit.expression
        if not isinstance(value, exp.Literal) or not str(value.this).isdigit() \
                or int(value.this) > MAX_ROWS:
            tree = tree.limit(MAX_ROWS)
    return tree.sql(dialect="postgres")
