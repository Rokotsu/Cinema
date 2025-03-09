from fastapi import APIRouter, Depends, status, Response, Form
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta
from pydantic import EmailStr
from typing import Optional
from app.schemas.users import UserCreate, UserRead, UserUpdate, UserWithSubscription
from app.services.users_service import UserService
from app.services.subscriptions_service import SubscriptionService
from app.schemas.subscriptions import SubscriptionRead
from app.database.dependencies import get_db_session
from app.exceptions.custom_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    NoUpdateDataException,
    AuthenticationException
)
from app.core.security import verify_password, create_access_token, get_current_user
from app.models.users import User

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service() -> UserService:
    return UserService()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    email: EmailStr = Form(..., example="user@example.com"),
    username: str = Form(..., example="john_doe"),
    password: str = Form(..., min_length=8, example="secret123"),
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service)
):
    """
    Регистрирует нового пользователя.
    """
    user_in = UserCreate(email=email, username=username, password=password)
    return await user_service.register_user(db, user_in)

@router.get("/me", response_model=UserWithSubscription)
async def get_me_info(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """
    Возвращает информацию о залогиненном пользователе, включая активную подписку.
    """
    subscription_service = SubscriptionService()
    subscriptions = await subscription_service.list_subscriptions(db, skip=0, limit=100)
    user_sub = next(
        (sub for sub in subscriptions if sub.user_id == current_user.id and sub.status.value.lower() == "active"), None
    )
    now = datetime.now(timezone.utc)
    if user_sub:
        end_date = user_sub.end_date if user_sub.end_date else (user_sub.start_date + timedelta(days=30))
        remaining_days = (end_date - now).days
        if remaining_days < 0:
            remaining_days = 0
        msg = "Подписка активна"
    else:
        remaining_days = 0
        msg = "Подписка отсутствует"
    return UserWithSubscription(
        user=UserRead.from_orm(current_user),
        subscription=SubscriptionRead.from_orm(user_sub) if user_sub else None,
        remaining_days=remaining_days,
        message=msg
    )

@router.post("/login")
async def login(
    response: Response,
    username: str = Form(..., example="john_doe"),
    password: str = Form(..., example="secret123"),
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service)
):
    """
    Авторизует пользователя и возвращает access_token.
    """
    try:
        user = await user_service.get_user_by_username(db, username)
    except UserNotFoundException:
        raise AuthenticationException("Неверные учетные данные")
    if not verify_password(password, user.hashed_password):
        raise AuthenticationException("Неверные учетные данные")
    token = create_access_token({"sub": str(user.id)})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=900,
        expires=900,
        samesite="lax"
    )
    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    """
    Разлогинивает пользователя.
    """
    response.delete_cookie("access_token")
    return {"message": "Вы успешно разлогинились"}

@router.post("/confirm_age")
async def confirm_age(response: Response):
    """
    Подтверждает возраст пользователя.
    """
    response.set_cookie(key="age_confirmed", value="true", httponly=True)
    return {"message": "Возраст подтверждён"}

@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service)
):
    """
    Возвращает данные пользователя по его идентификатору.
    """
    return await user_service.get_user_by_id(db, user_id)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    email: Optional[EmailStr] = Form(None, example="newemail@example.com"),
    username: Optional[str] = Form(None, example="newusername"),
    password: Optional[str] = Form(None, min_length=8, example="newsecret123"),
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service)
):
    """
    Обновляет данные пользователя.
    """
    update_data = {}
    if email is not None:
        update_data["email"] = email
    if username is not None:
        update_data["username"] = username
    if password is not None:
        update_data["password"] = password
    if not update_data:
        raise NoUpdateDataException()
    user_update = UserUpdate(**update_data)
    return await user_service.update_user(db, user_id, user_update)
