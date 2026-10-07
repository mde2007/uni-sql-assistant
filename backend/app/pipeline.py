import time
import uuid

import asyncpg

from app import db
from app.config import PAGE_SIZE, MAX_ROWS
from app.llm import generate_sql, generate_answer
from app.validator import validate_sql, ValidationError
from app.explain import explain_sql
from app.schema_info import SCHEMA_TEXT
from app.logger import log_event

# Проверенные запросы для пагинации: query_id -> SQL
saved_queries = {}


def error_response(message, sql=None):
    return {"error": message, "sql": sql}


async def handle_question(question, session_id):
    log_event("question", session_id=session_id, question=question)

    # 1. Модель пишет SQL
    try:
        raw_sql = await generate_sql(question, SCHEMA_TEXT)
    except Exception as e:
        log_event("llm_error", session_id=session_id, error=str(e))
        return error_response("Модель недоступна, попробуйте позже.")

    if raw_sql is None:
        return error_response("Вопрос не относится к базе данных университета.")

    # 2. Проверка безопасности
    try:
        safe_sql = validate_sql(raw_sql)
    except ValidationError as e:
        log_event("sql_rejected", session_id=session_id, sql=raw_sql, reason=str(e))
        return error_response(f"Запрос отклонён проверкой безопасности: {e}", raw_sql)

    # 3. Выполнение в базе
    start = time.perf_counter()
    try:
        total = await db.count_rows(safe_sql)
        columns, rows = await db.fetch_page(safe_sql, PAGE_SIZE, 0)
    except asyncpg.exceptions.QueryCanceledError:
        log_event("db_timeout", session_id=session_id, sql=safe_sql)
        return error_response(
            "Запрос выполнялся дольше 5 секунд и был остановлен. Уточните вопрос.",
            safe_sql,
        )
    except Exception as e:
        log_event("db_error", session_id=session_id, sql=safe_sql, error=str(e))
        return error_response("Ошибка при выполнении запроса. Ответ не сформирован.", safe_sql)

    duration_ms = round((time.perf_counter() - start) * 1000)
    log_event("query_done", session_id=session_id, sql=safe_sql, rows=total, ms=duration_ms)

    query_id = uuid.uuid4().hex
    saved_queries[query_id] = safe_sql

    # 4. Текстовый ответ: в модель уходят только первые 20 строк
    try:
        answer = await generate_answer(question, columns, rows[:20], total)
    except Exception:
        answer = f"Найдено строк: {total}."

    try:
        explanation = explain_sql(safe_sql)
    except Exception:
        explanation = {}

    warning = None
    if total >= MAX_ROWS:
        warning = (
            f"Найдено {MAX_ROWS} строк или больше, показаны первые {PAGE_SIZE}. "
            "Уточните запрос: добавьте год, факультет или направление."
        )

    return {
        "query_id": query_id,
        "answer": answer,
        "sql": safe_sql,
        "explanation": explanation,
        "columns": columns,
        "rows": rows,
        "total_rows": total,
        "page": 1,
        "page_size": PAGE_SIZE,
        "warning": warning,
        "error": None,
    }


async def get_page(query_id, page):
    sql = saved_queries.get(query_id)
    if sql is None:
        return error_response("Результат устарел, задайте вопрос заново.")

    page = max(page, 1)
    offset = (page - 1) * PAGE_SIZE
    columns, rows = await db.fetch_page(sql, PAGE_SIZE, offset)
    total = await db.count_rows(sql)
    log_event("page", query_id=query_id, page=page)

    return {
        "query_id": query_id,
        "columns": columns,
        "rows": rows,
        "total_rows": total,
        "page": page,
        "page_size": PAGE_SIZE,
        "error": None,
    }