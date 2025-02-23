from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.payments import PaymentCreate, PaymentRead, PaymentUpdate
from app.services.payments_dao import PaymentService
from app.database.dependencies import get_db_session
from app.exceptions.custom_exceptions import PaymentNotFoundException

router = APIRouter(prefix="/payments", tags=["payments"])
payment_service = PaymentService()

@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(payment_in: PaymentCreate, db: AsyncSession = Depends(get_db_session)):
    return await payment_service.create_payment(db, payment_in)

@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(payment_id: int, db: AsyncSession = Depends(get_db_session)):
    try:
        return await payment_service.get_payment(db, payment_id)
    except PaymentNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/{payment_id}", response_model=PaymentRead)
async def update_payment(payment_id: int, payment_in: PaymentUpdate, db: AsyncSession = Depends(get_db_session)):
    try:
        return await payment_service.update_payment(db, payment_id, payment_in)
    except PaymentNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
