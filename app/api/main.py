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
