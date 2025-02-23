from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.subscriptions import SubscriptionCreate, SubscriptionRead, SubscriptionUpdate
from app.services.subscriptions_service import SubscriptionService
from app.database.dependencies import get_db_session
from app.exceptions.custom_exceptions import SubscriptionNotFoundException

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
subscription_service = SubscriptionService()

@router.post("/", response_model=SubscriptionRead, status_code=status.HTTP_201_CREATED)
async def create_subscription(sub_in: SubscriptionCreate, db: AsyncSession = Depends(get_db_session)):
    return await subscription_service.create_subscription(db, sub_in)

@router.get("/{subscription_id}", response_model=SubscriptionRead)
async def get_subscription(subscription_id: int, db: AsyncSession = Depends(get_db_session)):
    try:
        return await subscription_service.get_subscription(db, subscription_id)
    except SubscriptionNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/{subscription_id}", response_model=SubscriptionRead)
async def update_subscription(subscription_id: int, sub_in: SubscriptionUpdate, db: AsyncSession = Depends(get_db_session)):
    try:
        return await subscription_service.update_subscription(db, subscription_id, sub_in)
    except SubscriptionNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
