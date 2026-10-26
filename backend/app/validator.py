import sqlglot
from sqlglot import exp

try:
    from app.config import MAX_ROWS
except Exception:
    MAX_ROWS = 1000

ALLOWED_TABLES = {
    "v_applications", "v_students", "v_grades", "v_teachers",
    "faculties", "departments", "programs", "disciplines",
}

# Список функций:
ALLOWED_FUNCTIONS = {
    # агрегаты
    "count", "sum", "avg", "min", "max", "stddev", "percentile_cont", "mode",
    "group_concat", "string_agg", "array_agg", "logical_and",
    # оконные
    "row_number", "rank", "dense_rank", "lag", "lead",
    # математика
    "round", "abs", "floor", "ceil", "power", "sqrt", "ln", "mod",
    # строки
    "lower", "upper", "length", "trim", "substring", "replace", "concat",
    "left", "right", "split_part", "str_position",
    # даты
    "extract", "date_part", "timestamp_trunc", "date_trunc", "time_to_str", "to_char",
    "current_date", "current_timestamp", "age", "make_date",
    # логика и типы
    "and", "or", "case", "if", "coalesce", "nullif", "greatest", "least", "cast",
}


class ValidationError(Exception):
    pass


def validate_sql(sql):
    """Возвращает безопасный SQL с LIMIT или бросает ValidationError."""
    sql = (sql or "").strip().rstrip(";").strip()
    if not sql:
        raise ValidationError("пустой запрос")

    try:
        statements = sqlglot.parse(sql, read="postgres")
    except sqlglot.errors.SqlglotError:
        raise ValidationError("не удалось разобрать SQL")

    if len(statements) != 1 or statements[0] is None:
        raise ValidationError("разрешён ровно один запрос")
    tree = statements[0]

    if not isinstance(tree, (exp.Select, exp.Union)):
        raise ValidationError("разрешены только запросы SELECT")

    if tree.find(exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create,
                exp.Command, exp.Into) is not None:
        raise ValidationError("запрещённая команда внутри запроса")

    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    for table in tree.find_all(exp.Table):
        name = table.name.lower()
        if not table.db and name in cte_names:
            continue  # временная таблица из WITH
        if table.db and table.db.lower() != "api":
            raise ValidationError(f"схема {table.db} запрещена")
        if name not in ALLOWED_TABLES:
            raise ValidationError(f"таблица {name} запрещена")

    for func in tree.find_all(exp.Func):
        fname = (func.name if isinstance(func, exp.Anonymous) else func.sql_name()).lower()
        if fname not in ALLOWED_FUNCTIONS:
            raise ValidationError(f"функция {fname} запрещена")

    if tree.find(exp.Dot) is not None:
        raise ValidationError("обращение к полям через точку запрещено")
    row_names = {table.name.lower() for table in tree.find_all(exp.Table)}
    row_names |= {alias.name.lower() for alias in tree.find_all(exp.TableAlias) if alias.name}
    output_aliases = {alias.alias.lower() for alias in tree.find_all(exp.Alias)}
    for col in tree.find_all(exp.Column):
        name = col.name.lower()
        if col.table or name not in row_names:
            continue
        if name in output_aliases and col.find_ancestor(exp.Order) is not None:
            continue  # ORDER BY по имени столбца из SELECT, например AS programs
        raise ValidationError(f"ссылка на всю строку таблицы {name} запрещена")

    for sel in tree.find_all(exp.Select):
        for column in sel.expressions:
            has_aggregate = column.find(exp.AggFunc) is not None
            if column.find(exp.Star) is not None and not has_aggregate:
                raise ValidationError("SELECT * запрещён, нужно перечислить столбцы")

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
