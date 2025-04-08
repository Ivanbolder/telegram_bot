import asyncio
from aiogram import types
from aiogram.dispatcher import Dispatcher
from config import ADMIN_ID
from database import *
from utils import gender_keyboard, edit_options_keyboard, like_dislike_keyboard

user_states = {}

async def start(message: types.Message):
    user_id = str(message.from_user.id)
    user_states[user_id] = {"step": "name", "data": {}}
    await message.answer("Введите имя:")

async def handle_text(message: types.Message):
    user_id = str(message.from_user.id)
    state = user_states.get(user_id)
    if not state:
        return await message.answer("Пожалуйста, начните с команды /start")

    step = state.get("step")
    data = state.get("data", {})

    if step == "name":
        data["name"] = message.text
        state["step"] = "surname"
        await message.answer("Введите фамилию:")
    elif step == "surname":
        data["surname"] = message.text
        state["step"] = "age"
        await message.answer("Введите возраст:")
    elif step == "age":
        data["age"] = message.text
        state["step"] = "gender"
        await message.answer("Выберите пол:", reply_markup=gender_keyboard())
    elif step == "gender":
        data["gender"] = message.text
        state["step"] = "birth"
        await message.answer("Введите дату рождения:")
    elif step == "birth":
        data["birth"] = message.text
        state["step"] = "bio"
        await message.answer("Напишите немного о себе:")
    elif step == "bio":
        data["bio"] = message.text
        state["step"] = "photo"
        await message.answer("Отправьте фотографию:")
    elif step == "edit":
        field = message.text.lower()
        valid = ["имя", "фамилия", "возраст", "пол", "дата рождения", "о себе", "фото"]
        if field in valid:
            state["step"] = "edit_value"
            state["field"] = field
            if field == "фото":
                await message.answer("Отправьте новое фото:")
            else:
                await message.answer("Введите новое значение:")
        else:
            await message.answer("Некорректный выбор поля.")
    elif step == "edit_value":
        profile = get_user(user_id)
        field_map = {
            "имя": "name", "фамилия": "surname", "возраст": "age",
            "пол": "gender", "дата рождения": "birth", "о себе": "bio"
        }
        db_field = field_map.get(state.get("field"))
        if db_field:
            profile[db_field] = message.text
            save_user(user_id, profile)
            await message.answer("✅ Обновлено.")
        user_states.pop(user_id, None)
    elif step == "search":
        results = find_user_by_name(message.text)
        if not results:
            await message.answer("❌ Не найдено.")
        else:
            for uid in results:
                await send_profile(message, uid, user_id)
        user_states.pop(user_id, None)

async def handle_photo(message: types.Message):
    user_id = str(message.from_user.id)
    state = user_states.get(user_id)
    if not state:
        return
    step = state.get("step")
    if step == "photo":
        state["data"]["photo"] = message.photo[-1].file_id
        state["data"]["username"] = message.from_user.username or "без username"
        save_user(user_id, state["data"])
        user_states.pop(user_id)
        await message.answer("✅ Анкета сохранена!")
    elif step == "edit_value" and state.get("field") == "фото":
        profile = get_user(user_id)
        profile["photo"] = message.photo[-1].file_id
        save_user(user_id, profile)
        await message.answer("✅ Фото обновлено!")
        user_states.pop(user_id)

async def send_profile(message, target_id, viewer_id=None):
    profile = get_user(target_id)
    if not profile:
        return await message.answer("Анкета не найдена.")
    like, dislike = get_likes_info(target_id)
    text = (
        f"👤 {profile['name']} {profile['surname']} (@{profile.get('username', '')})\n"
        f"🎂 {profile['birth']} ({profile['age']} лет)\n"
        f"⚥ {profile['gender']}\n"
        f"📝 {profile['bio']}\n"
        f"👍 {like}   👎 {dislike}"
    )
    keyboard = like_dislike_keyboard(viewer_id, target_id)
    await message.answer_photo(profile["photo"], caption=text, reply_markup=keyboard)

async def myanketa(message: types.Message):
    await send_profile(message, str(message.from_user.id), str(message.from_user.id))

async def edit_profile(message: types.Message):
    user_id = str(message.from_user.id)
    user_states[user_id] = {"step": "edit"}
    await message.answer("Что хотите изменить?", reply_markup=edit_options_keyboard())

async def search_user(message: types.Message):
    user_states[str(message.from_user.id)] = {"step": "search", "data": {}}
    await message.answer("Введите имя или фамилию для поиска:")

async def top_users(message: types.Message):
    top = get_top_users()
    if not top:
        return await message.answer("Пока нет анкет.")
    text = "🏆 <b>Топ по лайкам:</b>\n\n"
    for i, (uid, profile) in enumerate(top[:10], 1):
        likes, _ = get_likes_info(uid)
        text += f"{i}. {profile['name']} {profile['surname']} — 👍 {likes}\n"
    await message.answer(text, parse_mode="HTML")

async def counter(message: types.Message):
    await message.answer(f"👥 Всего пользователей: {len(get_all_users())}")

async def like_callback(call: types.CallbackQuery):
    user_id = str(call.from_user.id)
    msg = call.message
    if not msg.photo:
        return
    target_id = None
    for uid, profile in get_all_users().items():
        if profile.get("photo") == msg.photo[-1].file_id:
            target_id = uid
            break
    if not target_id or target_id == user_id:
        await call.answer("⛔ Нельзя голосовать за свою анкету.", show_alert=True)
        return
    value = 1 if call.data == "like" else -1
    like_profile(user_id, target_id, value)
    await call.answer("Голос учтён!")

async def allankets(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Только для админа.")
    users = get_all_users()
    if not users:
        return await message.answer("Нет анкет.")
    text = "📋 Все анкеты:\n\n"
    for u in users.values():
        text += f"{u['name']} {u['surname']}\n"
    await message.answer(text)

async def delete_by_name(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Только для админа.")
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("Укажи имя после команды, например: /delete_by_name Иван")
    name = parts[1]
    deleted = delete_user_by_name(name)
    await message.answer(f"Удалено анкет: {deleted}")

async def delete_all(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Только для админа.")
    delete_all_users()
    await message.answer("Все анкеты удалены.")

async def help_command(message: types.Message):
    text = (
        "<b>Команды:</b>\n"
        "/start — регистрация анкеты\n"
        "/myanketa — показать свою анкету\n"
        "/edit — редактировать анкету\n"
        "/search — поиск по имени\n"
        "/top — топ по лайкам\n"
        "/counter — количество пользователей\n"
        "/help — помощь по командам"
    )
    if message.from_user.id == ADMIN_ID:
        text += (
            "\n\n<b>Команды админа:</b>\n"
            "/allankets — список всех анкет\n"
            "/delete_by_name — удалить по имени\n"
            "/delete_all — удалить все анкеты"
        )
    await message.answer(text, parse_mode="HTML")

def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(prepare_delete_profile, lambda c: c.data.startswith("prepare_delete_"))
    dp.register_callback_query_handler(confirm_delete_profile, lambda c: c.data.startswith("confirm_delete_"))
    dp.register_callback_query_handler(cancel_delete, lambda c: c.data == "cancel_delete")
    dp.register_message_handler(start, commands=["start"])
    dp.register_message_handler(myanketa, commands=["myanketa"])
    dp.register_message_handler(edit_profile, commands=["edit"])
    dp.register_message_handler(search_user, commands=["search"])
    dp.register_message_handler(top_users, commands=["top"])
    dp.register_message_handler(counter, commands=["counter"])
    dp.register_message_handler(help_command, commands=["help"])
    dp.register_message_handler(allankets, commands=["allankets"])
    dp.register_message_handler(delete_all, commands=["delete_all"])
    dp.register_message_handler(delete_by_name, commands=["delete_by_name"])
    dp.register_callback_query_handler(like_callback)
    dp.register_message_handler(handle_photo, content_types=["photo"])
    dp.register_message_handler(handle_text, content_types=["text"])

# === Удаление по имени с подтверждением ===
from database import load_data, save_data



async def prepare_delete_profile(call: types.CallbackQuery):
    uid = call.data.split("_")[-1]
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Да", callback_data=f"confirm_delete_{uid}"),
        types.InlineKeyboardButton("❌ Нет", callback_data="cancel_delete")
    )
    await call.message.edit_caption("❗ Подтвердите удаление анкеты:", parse_mode="HTML", reply_markup=markup)

async def confirm_delete_profile(call: types.CallbackQuery):
    uid = call.data.split("_")[-1]
    data = load_data()
    if uid in data:
        del data[uid]
        save_data(data)
        await call.message.edit_caption("🗑️ Анкета удалена.", parse_mode="HTML")
    else:
        await call.message.edit_caption("❌ Анкета уже удалена или не найдена.", parse_mode="HTML")

async def cancel_delete(call: types.CallbackQuery):
    await call.message.edit_caption("❎ Удаление отменено.", parse_mode="HTML")