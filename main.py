from fastapi import FastAPI
from routers import users # пример подключения роутеров

# Создаем приложение FastAPI
app = FastAPI()

# пример регистрации роутеров с уникальными префиксами
# app.include_router(courses.router, prefix="/courses", tags=["Courses"])
app.include_router(users.router, prefix="/users", tags=["Users"])
# app.include_router(enrollments.router, prefix="/enrollments", tags=["Enrollments"])


# Тестовый эндпоинт
@app.get("/")
async def root():
    return {"message": "API is running!"}