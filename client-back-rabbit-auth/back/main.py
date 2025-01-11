from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import aio_pika
import json
import uuid
from models import User
from fastapi.responses import JSONResponse
import uvicorn
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#функция для отправки сообщений в RabbitMQ
async def send_to_rabbitmq(queue_name, message, response_queue):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")   #порт отдельно не указывается, т.к. используется стандартный 5672
    async with connection:
        channel = await connection.channel()
        #создаем очередь, если ее нет
        await channel.declare_queue(queue_name, durable=True)
        #генерируем уникальный ID для отслеживания ответа
        correlation_id = str(uuid.uuid4())
        #отправляем сообщение в очередь
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),  # Тело сообщения
                reply_to=response_queue,  # Указываем очередь для ответа
                correlation_id=correlation_id,  # Уникальный ID для ответа
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # Сообщение сохраняется (персистентность)
            ),
            routing_key=queue_name,
        )
    return correlation_id

#функция для получения ответа из RabbitMQ
async def get_response(response_queue, correlation_id):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(response_queue, durable=True)
        #ожидаем ответ с нужным correlation_id
        async for message in queue:
            if message.properties.correlation_id == correlation_id:
                return json.loads(message.body.decode())   #возвращаем ответ как словарь

#обработчик регистрации
@app.post("/registration")
async def registration_handler(user: User):
    print("Пришли данные регистрации:")
    print(user.email)
    print(user.password)

    #очередь для получения ответа от сервиса аутентификации
    response_queue = "registration_response_queue"
    #отправляем запрос в RabbitMQ и получаем correlation_id
    correlation_id = await send_to_rabbitmq("registration_queue", {"email": user.email, "password": user.password}, response_queue)
    #получаем ответ от RabbitMQ
    response = await get_response(response_queue, correlation_id)
    #проверяем статус ответа
    if response["status"] == "success":
        return JSONResponse(content={"message": "Регистрация прошла успешно!"}, status_code=200)
    else:
        return JSONResponse(content={"message": response["message"]}, status_code=202)

#обработчик авторизации
@app.post("/authorization")
async def authorization_handler(user: User):
    print("Пришли данные авторизации:")
    print(user.email)
    print(user.password)

    #очередь для получения ответа от сервиса аутентификации
    response_queue = "authorization_response_queue"
    #отправляем запрос в RabbitMQ и получаем correlation_id
    correlation_id = await send_to_rabbitmq("authorization_queue", {"email": user.email, "password": user.password}, response_queue)
    #получаем ответ от RabbitMQ
    response = await get_response(response_queue, correlation_id)
    #проверяем статус ответа
    if response["status"] == "success":
        return JSONResponse(content={"message": "Авторизация прошла успешно!"}, status_code=200)
    else:
        return JSONResponse(content={"message": response["message"]}, status_code=202)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)