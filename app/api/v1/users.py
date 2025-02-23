from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, create_access_token
from app.schemas.users import UserCreate, UserRead, UserUpdate, LoginForm
from app.services.users_service import UserService
from app.database.dependencies import get_db_session
from app.exceptions.custom_exceptions import UserAlreadyExistsException, UserNotFoundException

router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)):
    try:
        return await user_service.register_user(db, user_in)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db_session)):
    try:
        return await user_service.get_user_by_id(db, user_id)
    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user_in: UserUpdate, db: AsyncSession = Depends(get_db_session)):
    try:
        return await user_service.update_user(db, user_id, user_in)
    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

# Исправленный эндпоинт логина:
@router.post("/login")
async def login(
    form_data: LoginForm = Body(...),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        # Используем метод для поиска по username
        user = await user_service.get_user_by_username(db, form_data.username)
    except UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
