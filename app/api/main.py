# File: app/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import users, movies, subscriptions, payments, reviews  # добавлен reviews

app = FastAPI(
    title="Онлайн кинотеатр",
    description="API для онлайн кинотеатра на FastAPI",
    version="1.0.0"
)

# Подключение CORS, чтобы запросы к API могли приходить из браузера
origins = [
    # 3000 - порт, на котором работает фронтенд на React.js
    "http://localhost:3000",
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

app.include_router(users.router)
app.include_router(movies.router)
app.include_router(subscriptions.router)
app.include_router(payments.router)
app.include_router(reviews.router)
@app.get("/success")
async def payment_success(session_id: str):
    return {"message": "Оплата прошла успешно!", "session_id": session_id}

@app.get("/cancel")
async def payment_cancel():
    return {"message": "Оплата отменена."}
