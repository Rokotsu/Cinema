# File: app/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1 import users, movies, subscriptions, payments, reviews
from app.routes import html_routes

app = FastAPI(
    title="Онлайн кинотеатр",
    description="API для онлайн кинотеатра на FastAPI",
    version="1.0.0"
)

# Подключение CORS, чтобы запросы к API могли приходить из браузера
origins = [
    "http://localhost:3000",  # если фронтенд на React, например
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

# Монтирование статики: файлы из папки "static" будут доступны по /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключение API-маршрутов
app.include_router(users.router)
app.include_router(movies.router)
app.include_router(subscriptions.router)
app.include_router(payments.router)
app.include_router(reviews.router)

# Подключение маршрутов фронтенда (HTML страницы)
app.include_router(html_routes.router)

@app.get("/success")
async def payment_success(session_id: str):
    return {"message": "Оплата прошла успешно!", "session_id": session_id}

@app.get("/cancel")
async def payment_cancel():
    return {"message": "Оплата отменена."}
