from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from models import User
from schemas import UserCreate

# CRUD для пользователей
async def create_user(db: AsyncSession, user_data: UserCreate):
    """Создаёт пользователя или возвращает существующего."""
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return existing_user  # Пользователь уже существует, возвращаем его

    # Если пользователя нет, создаём нового
    new_user = User(name=user_data.name, email=user_data.email)
    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании пользователя: {str(e)}")

    return new_user


async def get_users(db: AsyncSession):
    """Получить всех пользователей."""
    result = await db.execute(select(User))
    return result.scalars().all()