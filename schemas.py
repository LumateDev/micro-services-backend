from pydantic import BaseModel, EmailStr
from datetime import datetime

# Базовая схема пользователя
class UserBase(BaseModel):
    name: str
    email: EmailStr

# Схема для создания пользователя
class UserCreate(UserBase):
    pass

# Схема для ответа
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
