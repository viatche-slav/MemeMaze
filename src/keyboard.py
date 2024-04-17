from telebot import types

keyboard = types.InlineKeyboardMarkup()
keyboard.add(types.InlineKeyboardButton(text="Move left", callback_data="left"))
keyboard.add(types.InlineKeyboardButton(text="Move forward", callback_data="forward"))
keyboard.add(types.InlineKeyboardButton(text="Move right", callback_data="right"))
