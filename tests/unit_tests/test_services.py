# tests/test_services.py

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.users_service import UserService
from app.services.movies_service import MovieService
from app.services.subscriptions_service import SubscriptionService
from app.services.payments_dao import PaymentService

from app.schemas.users import UserCreate, UserUpdate
from app.schemas.movies import MovieCreate, MovieUpdate
from app.schemas.subscriptions import SubscriptionCreate, SubscriptionUpdate
from app.schemas.payments import PaymentCreate, PaymentUpdate

from app.exceptions.custom_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    MovieNotFoundException,
    SubscriptionNotFoundException,
    PaymentNotFoundException,
)


# Тесты для UserService

@pytest.mark.asyncio
async def test_user_service_register_get(db_session: AsyncSession):
    user_service = UserService()
    user_in = UserCreate(email="service_user@example.com", username="serviceUser", password="secret123")
    user = await user_service.register_user(db_session, user_in)
    assert user.id is not None
    # Получаем пользователя через сервис
    fetched = await user_service.get_user_by_id(db_session, user.id)
    assert fetched.email == "service_user@example.com"


@pytest.mark.asyncio
async def test_user_service_duplicate_registration(db_session: AsyncSession):
    user_service = UserService()
    user_in = UserCreate(email="dup_user@example.com", username="dupUser", password="secret123")
    await user_service.register_user(db_session, user_in)
    with pytest.raises(UserAlreadyExistsException):
        await user_service.register_user(db_session, user_in)


@pytest.mark.asyncio
async def test_user_service_update(db_session: AsyncSession):
    user_service = UserService()
    user_in = UserCreate(email="update_user@example.com", username="updateUser", password="secret123")
    user = await user_service.register_user(db_session, user_in)
    update_data = UserUpdate(email="updated_user@example.com")
    updated = await user_service.update_user(db_session, user.id, update_data)
    assert updated.email == "updated_user@example.com"


# Тесты для MovieService

@pytest.mark.asyncio
async def test_movie_service_create_update_get(db_session: AsyncSession):
    movie_service = MovieService()
    movie_in = MovieCreate(title="Test Movie", description="A test movie", duration=100, rating=7.0)
    movie = await movie_service.create_movie(db_session, movie_in)
    assert movie.id is not None
    update_data = MovieUpdate(title="Updated Test Movie", rating=8.0)
    updated = await movie_service.update_movie(db_session, movie.id, update_data)
    assert updated.title == "Updated Test Movie"
    fetched = await movie_service.get_movie(db_session, movie.id)
    assert fetched.id == movie.id


# Тесты для SubscriptionService

@pytest.mark.asyncio
async def test_subscription_service_create_update_get(db_session: AsyncSession):
    # Для подписок сначала создадим пользователя, чтобы получить корректный user_id
    user_service = UserService()
    user_in = UserCreate(email="sub_service@example.com", username="subService", password="secret123")
    user = await user_service.register_user(db_session, user_in)

    sub_service = SubscriptionService()
    sub_in = SubscriptionCreate(user_id=user.id, plan="Premium")
    subscription = await sub_service.create_subscription(db_session, sub_in)
    assert subscription.id is not None
    update_data = SubscriptionUpdate(plan="Basic")
    updated = await sub_service.update_subscription(db_session, subscription.id, update_data)
    assert updated.plan == "Basic"
    fetched = await sub_service.get_subscription(db_session, subscription.id)
    assert fetched.id == subscription.id


# Тесты для PaymentService

@pytest.mark.asyncio
async def test_payment_service_create_update_get(db_session: AsyncSession):
    # Для платежей также создадим пользователя
    user_service = UserService()
    user_in = UserCreate(email="pay_service@example.com", username="payService", password="secret123")
    user = await user_service.register_user(db_session, user_in)

    pay_service = PaymentService()
    pay_in = PaymentCreate(user_id=user.id, amount=59.99, payment_method="robokassa")
    payment = await pay_service.create_payment(db_session, pay_in)
    assert payment.id is not None
    update_data = PaymentUpdate(status="completed", transaction_id="tx456")
    updated = await pay_service.update_payment(db_session, payment.id, update_data)
    assert updated.transaction_id == "tx456"
    fetched = await pay_service.get_payment(db_session, payment.id)
    assert fetched.id == payment.id
