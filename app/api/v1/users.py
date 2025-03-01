# File: app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Body, Response
from sqlalchemy.ext.asyncio import AsyncSession
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
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service)
):
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
    user_in: UserUpdate,
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
    form_data: LoginForm = Body(...),
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service)
):
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
