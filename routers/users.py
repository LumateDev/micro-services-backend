from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UserCreate, UserResponse
from crud import create_user, get_users
from database import get_db

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user_endpoint(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Создаёт пользователя или возвращает существующего."""
    return await create_user(db, user)


@router.get("/", response_model=list[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    """Получаем список всех пользователей."""
    return await get_users(db)
