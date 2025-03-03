# File: app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Form, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from app.schemas.users import UserCreate, UserRead, UserUpdate, LoginForm
from app.services.users_service import UserService
from app.database.dependencies import get_db_session
from app.exceptions.custom_exceptions import UserAlreadyExistsException, UserNotFoundException
from app.core.security import verify_password, create_access_token

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
    user_in = UserCreate(email=email, username=username, password=password)
    try:
        return await user_service.register_user(db, user_in)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.get_user_by_id(db, user_id)
    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_in: UserUpdate,  # PUT остаётся с JSON‑телом
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.update_user(db, user_id, user_in)
    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/login")
async def login(
    response: Response,
    username: str = Form(..., example="john_doe"),
    password: str = Form(..., example="secret123"),
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service)
):
    form_data = LoginForm(username=username, password=password)
    try:
        user = await user_service.get_user_by_username(db, form_data.username)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")
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
    response.delete_cookie("access_token")
    return {"message": "Вы успешно разлогинились"}

@router.post("/confirm_age")
async def confirm_age(response: Response):
    # Устанавливаем cookie, подтверждающее, что пользователю 18+
    response.set_cookie(key="age_confirmed", value="true", httponly=True)
    return {"message": "Возраст подтверждён"}
