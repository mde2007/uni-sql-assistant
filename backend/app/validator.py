# ЗАГЛУШКА. Заменит Студент 4.
class ValidationError(Exception):
    pass


def validate_sql(sql):
    return sql