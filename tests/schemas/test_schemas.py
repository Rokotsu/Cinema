# tests/test_schemas.py

import pytest
from datetime import datetime
from pydantic import ValidationError

# Импортируем схемы для пользователей
from app.schemas.users import UserCreate, UserUpdate, UserRead, UserRole

# Импортируем схемы для фильмов
from app.schemas.movies import MovieCreate, MovieUpdate, MovieRead

# Импортируем схемы для подписок
from app.schemas.subscriptions import SubscriptionCreate, SubscriptionUpdate, SubscriptionRead, SubscriptionStatus

# Импортируем схемы для платежей
from app.schemas.payments import PaymentCreate, PaymentUpdate, PaymentRead, PaymentStatus


### Тесты для пользователей

def test_user_create_valid():
    data = {
        "email": "user@example.com",
        "username": "testuser",
        "password": "strongpassword123"
    }
    user = UserCreate(**data)
    assert user.email == "user@example.com"
    assert user.username == "testuser"
    assert user.password == "strongpassword123"

def test_user_create_invalid_email():
    data = {
        "email": "not-an-email",
        "username": "testuser",
        "password": "strongpassword123"
    }
    with pytest.raises(ValidationError):
        UserCreate(**data)

def test_user_update_partial():
    data = {"email": "newemail@example.com"}
    update = UserUpdate(**data)
    assert update.email == "newemail@example.com"
    assert update.username is None

def test_user_read_orm_mode():
    now = datetime.utcnow()
    data = {
        "id": 1,
        "email": "user@example.com",
        "username": "testuser",
        "role": "user",  # или UserRole.USER, оба варианта работают
        "created_at": now,
        "updated_at": now,
    }
    user = UserRead(**data)
    assert user.id == 1
    assert user.role == "user"


### Тесты для фильмов

def test_movie_create_valid():
    data = {
        "title": "Inception",
        "description": "A mind-bending thriller",
        "duration": 148,
        "rating": 8.8
    }
    movie = MovieCreate(**data)
    assert movie.title == "Inception"
    assert movie.description == "A mind-bending thriller"

def test_movie_update():
    data = {"title": "Inception Updated", "rating": 9.0}
    update = MovieUpdate(**data)
    assert update.title == "Inception Updated"
    assert update.rating == 9.0

def test_movie_read():
    now = datetime.utcnow()
    data = {
        "id": 1,
        "title": "Inception",
        "description": "A mind-bending thriller",
        "release_date": now,
        "duration": 148,
        "rating": 8.8,
        "created_at": now,
        "updated_at": now,
    }
    movie = MovieRead(**data)
    assert movie.id == 1
    assert movie.title == "Inception"


### Тесты для подписок

def test_subscription_create():
    data = {
        "user_id": 1,
        "plan": "Premium",
        "start_date": datetime.utcnow()
    }
    sub = SubscriptionCreate(**data)
    assert sub.user_id == 1
    assert sub.plan == "Premium"
    # Если не передали status, по умолчанию должна быть ACTIVE
    assert sub.status == SubscriptionStatus.ACTIVE

def test_subscription_update():
    data = {"status": "expired"}
    sub_update = SubscriptionUpdate(**data)
    # Так как SubscriptionStatus наследуется от str, сравнение со строкой корректно
    assert sub_update.status == "expired"

def test_subscription_read():
    now = datetime.utcnow()
    data = {
        "id": 1,
        "user_id": 1,
        "plan": "Basic",
        "start_date": now,
        "end_date": now,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    sub_read = SubscriptionRead(**data)
    assert sub_read.id == 1
    assert sub_read.status == "active"


### Тесты для платежей

def test_payment_create():
    data = {
        "user_id": 1,
        "amount": 199.99,
        "payment_method": "robokassa"
    }
    pay = PaymentCreate(**data)
    assert pay.user_id == 1
    assert pay.amount == 199.99
    assert pay.payment_method == "robokassa"

def test_payment_update():
    data = {
        "status": "completed",
        "transaction_id": "tx12345"
    }
    pay_update = PaymentUpdate(**data)
    assert pay_update.status == "completed"
    assert pay_update.transaction_id == "tx12345"

def test_payment_read():
    now = datetime.utcnow()
    data = {
        "id": 1,
        "user_id": 1,
        "subscription_id": None,
        "amount": 199.99,
        "currency": "RUB",
        "payment_method": "robokassa",
        "status": "pending",
        "transaction_id": "tx12345",
        "created_at": now,
        "updated_at": now,
    }
    pay_read = PaymentRead(**data)
    assert pay_read.id == 1
    assert pay_read.status == "pending"
