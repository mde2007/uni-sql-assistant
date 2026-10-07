from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import db
from app.config import FRONTEND_DIR
from app.pipeline import handle_question, get_page


@asynccontextmanager
async def lifespan(app):
    await db.init_pool()    # при старте сервера
    yield
    await db.close_pool()   # при остановке


app = FastAPI(title="University SQL Assistant", lifespan=lifespan)

# Разрешаем виджету с других сайтов обращаться к нашему API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Файлы виджета будут доступны по адресу /static/...
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    session_id: str = "anonymous"


@app.post("/api/ask")
async def ask(request: AskRequest):
    return await handle_question(request.question, request.session_id)


@app.get("/api/result/{query_id}")
async def result(query_id: str, page: int = 1):
    return await get_page(query_id, page)


@app.get("/health")
async def health():
    return {"status": "ok"}