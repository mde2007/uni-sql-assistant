# Чат-ассистент для базы данных университета

Пользователь задаёт вопрос обычным языком, ассистент составляет SQL,
проверяет его, выполняет в PostgreSQL и показывает ответ, SQL и таблицу.

## Запуск

```bash
cp .env.example .env          # вписать ключ модели
docker compose up -d --build
pip install -r backend/requirements.txt
python db/seed/seed.py
```

Открыть http://localhost:8000/static/index.html
(проверка: http://localhost:8000/health, документация API: http://localhost:8000/docs)

Остановить: `docker compose down`. Сбросить базу: `docker compose down -v`.

## Архитектура

Виджет (HTML/JS) → FastAPI → модель → валидатор SQL → PostgreSQL (read-only)

## Безопасность (защита в глубину, 3 слоя)

1. Валидатор на sqlglot: только один SELECT, whitelist таблиц и схем,
   запрет опасных функций, запрет `SELECT *` и кодов студентов, LIMIT ≤ 1000.
2. Пользователь БД `assistant_ro`: только чтение, только обезличённые
   представления, `statement_timeout` 5 с.
3. Обезличенные представления: нет ФИО, паспортов и контактов студентов.

## Логи

Каждое действие пишется одной JSON-строкой в `logs/app.log`.

## Тесты

```bash
cd backend && pytest -v                    # автотесты валидатора (атаки)
locust -f load/locustfile.py --host http://localhost:8000   # нагрузка
```

## Команда

- Московский Даниил -backend, тимлид;
- Аббасов Аббас - база данных;
- Шафиков Юлай — виджет;
- Валеев Тимур — Docker, безопасность, тесты;
