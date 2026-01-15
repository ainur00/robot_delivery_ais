from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, robots, transport_requests, trajectories
from app.database import *
from app import models

# Создаем таблицы в БД
# drop_tables()
create_tables()

app = FastAPI(
    title="Robot Delivery System API",
    description="API для системы управления автономными роботами-доставщиками",
    version="1.0.0",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем только нужные роутеры
app.include_router(users.router)
app.include_router(robots.router)
app.include_router(transport_requests.router)
app.include_router(trajectories.router)


@app.get("/")
def root():
    return {
        "message": "Robot Delivery System API",
        "docs": "/docs",
        "version": "1.0.0",
        "endpoints": {
            "users": ["POST /users/register", "POST /users/login", "GET /users/me"],
            "robots": ["GET /robots/", "GET /robots/available", "PATCH /robots/{id}/occupy", "PATCH /robots/{id}/position"],
            "requests": ["GET /requests/my", "GET /requests/{id}", "POST /requests/", "PATCH /requests/{id}/status", "PATCH /requests/{id}/accept", "PATCH /requests/{id}/reject", "PATCH /requests/{id}/complete"],
            "trajectories": ["GET /trajectories/request/{request_id}", "POST /trajectories/"]
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}