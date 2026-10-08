import getpass
import os
import sys
from pathlib import Path

import psycopg

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "seed"))

HOST = "localhost"
PORT = 5432


def main():
    # python db/setup_db.py --reset  удаляет базу и создаёт её заново
    reset = "--reset" in sys.argv
    password = os.getenv("POSTGRES_PASSWORD") or getpass.getpass("Пароль пользователя postgres: ")

    # 1. Роль admin и база university
    with psycopg.connect(host=HOST, port=PORT, user="postgres", password=password,
                        dbname="postgres", autocommit=True) as conn:
        if reset:
            # WITH (FORCE) закрывает чужие подключения, например открытый DBeaver
            conn.execute("DROP DATABASE IF EXISTS university WITH (FORCE)")
            print("База university удалена")
        if conn.execute("SELECT 1 FROM pg_roles WHERE rolname = 'admin'").fetchone() is None:
            conn.execute("CREATE ROLE admin LOGIN SUPERUSER PASSWORD 'admin_password'")
            print("Роль admin создана")
        if conn.execute("SELECT 1 FROM pg_database WHERE datname = 'university'").fetchone() is None:
            conn.execute("CREATE DATABASE university OWNER admin ENCODING 'UTF8' TEMPLATE template0")
            print("База university создана")

    # 2. Таблицы, представления и права
    with psycopg.connect(host=HOST, port=PORT, user="admin", password="admin_password",
                        dbname="university", autocommit=True) as conn:
        tables_count = conn.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
        ).fetchone()[0]

        for path in sorted((BASE / "init").glob("*.sql")):
            if path.name.startswith(("01", "02")) and tables_count > 0:
                print("Пропускаю", path.name, "(таблицы уже есть)")
                continue
            conn.execute(path.read_text(encoding="utf-8"))
            print("Выполнен", path.name)

        grades_count = conn.execute("SELECT count(*) FROM grades").fetchone()[0]

    # 3. Данные, только если таблицы пустые
    if grades_count == 0:
        import seed
        seed.main()
    else:
        print("Данные уже есть, пропускаю seed.py")

    print("Готово. База university настроена.")


if __name__ == "__main__":
    main()