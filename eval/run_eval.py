import json
import sys

import httpx
import psycopg

API_URL = "http://localhost:8000/api/ask"
ADMIN_URL = "postgresql://admin:admin_password@localhost:5432/university"


def normalize_value(value):
    try:
        return str(round(float(value), 2))
    except (TypeError, ValueError):
        return str(value)


def normalize(rows):
    return sorted(tuple(normalize_value(v) for v in row) for row in rows)


def check_sql_only(questions):
    # Режим без сервера: проверяем, что все эталонные SQL выполняются
    with psycopg.connect(ADMIN_URL) as conn:
        for item in questions:
            if item.get("must_refuse"):
                print("отказ    ", item["question"])
                continue
            rows = conn.execute(item["expected_sql"]).fetchall()
            print(f"{len(rows)} строк  ", item["question"])


def run_full(questions):
    passed = 0
    with psycopg.connect(ADMIN_URL) as conn:
        for item in questions:
            response = httpx.post(
                API_URL,
                json={"question": item["question"], "session_id": "eval"},
                timeout=60,
            ).json()

            if item.get("must_refuse"):
                if response.get("error"):
                    passed += 1
                    print("OK (отказ)  ", item["question"])
                else:
                    print("ОПАСНО!     ", item["question"], "— система ответила")
                continue

            if response.get("error"):
                print("ОШИБКА      ", item["question"], "→", response["error"])
                continue

            expected = conn.execute(item["expected_sql"]).fetchall()
            if normalize(response["rows"]) == normalize(expected):
                passed += 1
                print("OK          ", item["question"])
            else:
                print("НЕВЕРНО     ", item["question"])
                print("    SQL модели:", response["sql"])

    print(f"\nИтого: {passed} из {len(questions)}")


def main():
    with open("eval/questions.json", encoding="utf-8") as f:
        questions = json.load(f)

    if "--check" in sys.argv:
        check_sql_only(questions)
    else:
        run_full(questions)


if __name__ == "__main__":
    main()