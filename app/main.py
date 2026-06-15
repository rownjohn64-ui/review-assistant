from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.db.session import engine
from app.db.base import Base
import os

app = FastAPI(title="Review Assistant")

# Создаем таблицы
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Подключаем маршруты
app.include_router(router)

# Шаблоны
templates = Jinja2Templates(directory="app/templates")

# Создаем папку для статики
os.makedirs("app/static", exist_ok=True)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "ok"}