import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import API_TOKEN
from handlers import register_handlers

# 🟢 Создаём бота
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# 🟢 Регистрируем хендлеры
register_handlers(dp)

# 🟢 FastAPI — фейковый веб-сервер для Render
from fastapi import FastAPI
import uvicorn

fake_api = FastAPI()

@fake_api.get("/")
async def root():
    return {"message": "Bot is running"}

async def start_bot():
    print("Бот запущен!")
    await dp.start_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    uvicorn.run(fake_api, host="0.0.0.0", port=10000)