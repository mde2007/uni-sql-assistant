import os
from dotenv import load_dotenv

load_dotenv()  # читает файл .env из корня проекта

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://assistant_ro:ro_password@localhost:5432/university",
)
FRONTEND_DIR = os.getenv("FRONTEND_DIR", "../frontend")

PAGE_SIZE = 50    # строк на одной странице таблицы
MAX_ROWS = 1000   # больше этого база не вернёт никогда