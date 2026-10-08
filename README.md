# Чат-ассистент для БД университета

Вопрос обычным языком → GigaChat составляет SQL → PostgreSQL → ответ текстом, с SQL и таблицей.

## Стек

- **Backend:** Python 3.13, FastAPI, uvicorn
- **База:** PostgreSQL 16
- **Модель:** GigaChat-2-Pro (API Сбера)
- **Разбор SQL:** sqlglot
- **Фронтенд:** HTML + JS виджет

## Безопасность

- Модель на вопросы о личных данных возвращает `NONE`, SQL не создаётся.
- Валидатор (`validator.py`) пропускает только один `SELECT`.
- Модель работает с обезличенными представлениями `v_*`: в них нет ФИО, паспортов и телефонов.
- Сервер подключается к базе под ролью `assistant_ro`: только чтение представлений, тайм-аут 5 секунд.
- Ключ GigaChat хранится в `.env`, который не попадает в Git.

## Запуск

Нужны Python 3.13 и PostgreSQL 16.

```powershell
git clone https://github.com/mde2007/uni-sql-assistant.git
cd uni-sql-assistant
python -m venv backend\.venv
backend\.venv\Scripts\activate
pip install -r backend\requirements.txt

python db\setup_db.py        # создаёт и заполняет базу, спросит пароль postgres
copy .env.example .env       # вписать GIGACHAT_AUTH_KEY

cd backend
uvicorn app.main:app --reload
```

Открыть http://localhost:8000/static/index.html
