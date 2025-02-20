# tests/test_dao.py

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.users_dao import UserDAO
from app.dao.movies_dao import MovieDAO
from app.dao.subscriptions_dao import SubscriptionDAO
from app.dao.payments_dao import PaymentDAO
from app.models.users import User
from app.models.movies import Movie
from app.models.subscriptions import Subscription
from app.models.payments import Payment

@pytest.mark.asyncio
async def test_user_dao_create_get(db_session: AsyncSession):
    user_dao = UserDAO()
    user_data = {
        "email": "dao_user@example.com",
        "username": "daoUser",
        "hashed_password": "hashedpassword"
    }
    # Создаем пользователя
    user = await user_dao.create(db_session, user_data)
    assert user.id is not None
    # Получаем по ID
    fetched = await user_dao.get_by_id(db_session, user.id)
    assert fetched is not None
    assert fetched.email == "dao_user@example.com"

@pytest.mark.asyncio
async def test_movie_dao_create_get(db_session: AsyncSession):
    movie_dao = MovieDAO()
    movie_data = {
        "title": "DAO Movie",
        "description": "Test movie DAO",
        "duration": 120,
        "rating": 8.0
    }
    movie = await movie_dao.create(db_session, movie_data)
    assert movie.id is not None
    fetched = await movie_dao.get_by_id(db_session, movie.id)
    assert fetched.title == "DAO Movie"

@pytest.mark.asyncio
async def test_subscription_dao_create_get(db_session: AsyncSession):
    sub_dao = SubscriptionDAO()
    # Для подписки нужен user_id, здесь используем произвольное значение
    sub_data = {
        "user_id": 1,
        "plan": "DAO Premium"
    }
    subscription = await sub_dao.create(db_session, sub_data)
    assert subscription.id is not None
    fetched = await sub_dao.get_by_id(db_session, subscription.id)
    assert fetched.plan == "DAO Premium"

@pytest.mark.asyncio
async def test_payment_dao_create_get(db_session: AsyncSession):
    pay_dao = PaymentDAO()
    pay_data = {
        "user_id": 1,
        "amount": 49.99,
        "payment_method": "dao_method"
    }
    payment = await pay_dao.create(db_session, pay_data)
    assert payment.id is not None
    fetched = await pay_dao.get_by_id(db_session, payment.id)
    assert fetched.amount == 49.99
