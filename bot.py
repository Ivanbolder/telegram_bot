import asyncio
from aiogram import Bot, Dispatcher, types
from config import API_TOKEN, ADMIN_ID
from handlers import register_handlers
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeChat

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

async def set_bot_commands(bot):
    user_commands = [
        BotCommand("start", "Начать регистрацию анкеты"),
        BotCommand("myanketa", "Показать свою анкету"),
        BotCommand("edit", "Редактировать анкету"),
        BotCommand("search", "Поиск по имени/фамилии"),
        BotCommand("top", "Топ по лайкам"),
        BotCommand("counter", "Количество пользователей"),
        BotCommand("help", "Помощь по командам")
    ]
    await bot.set_my_commands(user_commands, scope=BotCommandScopeAllPrivateChats())
    admin_commands = user_commands + [
        BotCommand("allankets", "Список всех анкет"),
        BotCommand("delete_by_name", "Удалить анкету по имени"),
        BotCommand("delete_all", "Удалить все анкеты")
    ]
    await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=ADMIN_ID))

async def main():
    print("Бот запущен!")
    await set_bot_commands(bot)
    register_handlers(dp)
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())