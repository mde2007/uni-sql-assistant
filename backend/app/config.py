import os
from dotenv import load_dotenv

load_dotenv()  # 

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://university_assistant:ro_password@localhost:5432/university",
)
FRONTEND_DIR = os.getenv("FRONTEND_DIR", "../frontend")

PAGE_SIZE = 50    # кол-во строк на одной странице таблицы
MAX_ROWS = 1000   # больше 1000 строк база никогда не вернет
SAVED_RESULTS = 200  # сколько последних результатов держим в памяти для пагинации