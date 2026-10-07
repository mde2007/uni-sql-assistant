# ЗАГЛУШКА МОДЕЛИ. Всегда возвращает один и тот же запрос.
# Названия функций и аргументы НЕ менять — настоящая модель будет такой же.

async def generate_sql(question: str, schema: str) -> str | None:
    # None означает: вопрос не про базу данных
    return (
        "SELECT p.name, count(*) AS applications "
        "FROM v_applications AS a "
        "JOIN programs AS p ON p.id = a.program_id "
        "WHERE a.year = 2026 "
        "GROUP BY p.name "
        "ORDER BY applications DESC"
    )


async def generate_answer(question: str, columns: list, rows: list, total: int) -> str:
    return f"Найдено строк: {total}."