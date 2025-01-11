import asyncio
import aio_pika
import json

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        #распаковываем сообщение
        data = json.loads(message.body)
        print(f"Обработано сообщение: {data}")
        #проверяем в какой очереди пришло сообщение
        if message.routing_key == "registration_queue":
            #логика для регистрации
            if "email" in data:
                #проверяем, что почта не равна "test@example.com" для регистрации
                if data["email"] == "test@example.com":
                    response = {"status": "failed", "message": "Пользователь с таким Email уже зарегистрирован!"}
                else:
                    response = {"status": "success", "message": "Регистрация прошла успешно!"}
            else:
                response = {"status": "failed", "message": "Отсутствуют обязательные поля для регистрации!"}
        elif message.routing_key == "authorization_queue":
            #логика для авторизации
            if "email" in data:
                #проверяем, что почта равна "test@example.com" для авторизации
                if data["email"] == "test@example.com":
                    response = {"status": "success", "message": "Авторизация прошла успешно!"}
                else:
                    response = {"status": "failed", "message": "Пользователь с таким Email не найден!"}
            else:
                response = {"status": "failed", "message": "Отсутствуют обязательные поля для авторизации!"}

        #отправляем ответ обратно в очередь, указанную в свойстве reply_to
        connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")   #порт не указываем, т.к. подразумевается стандартный 5672
        async with connection:
            channel = await connection.channel()
            #ответный message
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(response).encode(),
                    correlation_id=message.properties.correlation_id,   #уникальный ID для отслеживания
                ),
                routing_key=message.properties.reply_to,   #ответ отправляем в очередь, указанную в свойстве reply_to
            )
            print(f"Ответ отправлен: {response}")

async def main():
    #подключаемся к RabbitMQ
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")   #порт не указываем, т.к. подразумевается стандартный 5672
    async with connection:
        channel = await connection.channel()
        #слушаем очередь регистрации
        registration_queue = await channel.declare_queue("registration_queue", durable=True)
        await registration_queue.consume(process_message)
        #слушаем очередь авторизации
        authorization_queue = await channel.declare_queue("authorization_queue", durable=True)
        await authorization_queue.consume(process_message)
        print("Сервис авторизации запущен и слушает очереди...")
        await asyncio.Future()  #бесконечный цикл

if __name__ == "__main__":
    asyncio.run(main())
