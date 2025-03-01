# File: app/api/main.py
from fastapi import FastAPI
from app.api.v1 import users, movies, subscriptions, payments

app = FastAPI(
    title="Онлайн кинотеатр",
    description="API для онлайн кинотеатра на FastAPI",
    version="1.0.0"
)

app.include_router(users.router)
app.include_router(movies.router)
app.include_router(subscriptions.router)
app.include_router(payments.router)

# Новый endpoint для успешного завершения оплаты
@app.get("/success")
async def payment_success(session_id: str):
    return {"message": "Оплата прошла успешно!", "session_id": session_id}

# Новый endpoint для отмены оплаты
@app.get("/cancel")
async def payment_cancel():
    return {"message": "Оплата отменена."}
