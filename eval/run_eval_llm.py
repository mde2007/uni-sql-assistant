import asyncio
import json
import sys

import psycopg

sys.path.insert(0, "backend")

from app.llm import generate_sql  # noqa: E402
from app.schema_info import SCHEMA_TEXT  # noqa: E402

ADMIN_URL = "postgresql://admin:admin_password@localhost:5432/university"


def normalize_value(value):
    try:
        return str(round(float(value), 2))
    except (TypeError, ValueError):
        return str(value)


def normalize(rows):
    return sorted(tuple(normalize_value(v) for v in row) for row in rows)


def is_empty(rows):
    # Пусто: нет строк, или во всех ячейках NULL или 0
    for row in rows:
        for value in row:
            if value is not None and value != 0:
                return False
    return True


async def main():
    # python eval/run_eval_llm.py eval/questions_full.json
    path = sys.argv[1] if len(sys.argv) > 1 else "eval/questions.json"
    with open(path, encoding="utf-8") as f:
        questions = json.load(f)

    passed = 0
    with psycopg.connect(ADMIN_URL) as conn:
        conn.read_only = True  # модель не сможет ничего изменить

        for item in questions:
            sql = await generate_sql(item["question"], SCHEMA_TEXT)

            if item.get("must_refuse"):
                if sql is None:
                    passed += 1
                    print("OK (отказ)  ", item["question"])
                else:
                    print("ОПАСНО!     ", item["question"])
                    print("    SQL модели:", sql)
                continue

            # Такого в базе нет: модель не должна подменять похожим
            if item.get("no_data"):
                if sql is None:
                    passed += 1
                    print("OK (нет)    ", item["question"])
                    continue
                try:
                    actual = conn.execute(sql).fetchall()
                except Exception:
                    conn.rollback()
                    passed += 1
                    print("OK (нет)    ", item["question"])
                    continue
                if is_empty(actual):
                    passed += 1
                    print("OK (нет)    ", item["question"])
                else:
                    print("ВЫДУМАЛ     ", item["question"])
                    print("    SQL модели:", sql)
                    print("    Результат:", actual[:3])
                continue

            if sql is None:
                print("ОТКАЗ       ", item["question"], "(а надо ответить)")
                continue

            try:
                actual = conn.execute(sql).fetchall()
                expected = conn.execute(item["expected_sql"]).fetchall()
            except Exception as error:
                conn.rollback()
                print("ОШИБКА SQL  ", item["question"])
                print("    ", str(error).splitlines()[0])
                print("    SQL модели:", sql)
                continue

            if normalize(actual) == normalize(expected):
                passed += 1
                print("OK          ", item["question"])
            else:
                print("НЕВЕРНО     ", item["question"])
                print("    SQL модели:", sql)

    print(f"\nИтого: {passed} из {len(questions)}")


asyncio.run(main())
