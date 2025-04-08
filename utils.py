from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def gender_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("👨 Муж"), KeyboardButton("👩 Жен"))
    return kb

def edit_options_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("Имя", "Фамилия", "Возраст")
    kb.add("Пол", "Дата рождения", "О себе")
    kb.add("Фото", "Отмена")
    return kb

def like_dislike_keyboard(viewer_id, owner_id):
    if str(viewer_id) == str(owner_id):
        return None
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("👍", callback_data="like"),
        InlineKeyboardButton("👎", callback_data="dislike")
    )
    return kb