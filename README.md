Чат-ассистент для базы данных университета
Пользователь задаёт вопрос обычным языком, ассистент составляет SQL,
проверяет его, выполняет в PostgreSQL и показывает ответ с таблицей.

Запуск
```bash
cp .env.example .env # вписать ключ модели
docker compose up -d --build
pip install -r backend/requirements.txt
python db/seed/seed.py
```

Открыть http://localhost:8000/static/index.html

Архитектура
Виджет (HTML/JS) → FastAPI → модель → валидатор SQL → PostgreSQL (read-only)

Безопасность
Валидатор на sqlglot: только SELECT, whitelist таблиц, LIMIT 1000
Пользователь БД только для чтения, statement_timeout 5 с
Обезличенные представления: нет ФИО, паспортов и контактов студентов
Тесты
```bash
cd backend && pytest -v
```

Команда
Московский Даниил — backend, тимлид
Аббасов Аббас — база данных и безопасность
Шафиков Юлай — виджет
Валеев Тимур — Docker, тесты, презентация
