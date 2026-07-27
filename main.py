from fastapi import FastAPI
from database import engine, Base
import models

# Автоматически создаем таблицы в БД при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Volleyball League API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Volleyball League API is running with SQLite"}

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}
