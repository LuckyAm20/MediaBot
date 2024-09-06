import telebot

from bot_data import bot


def create_buttons(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
    keyboard.add(telebot.types.KeyboardButton(text='Поиск рекомендованных фильмов'),
                 telebot.types.KeyboardButton(text='Поиск рекомендованной музыки'),
                 telebot.types.KeyboardButton(text='Подборка топа'),
                 telebot.types.KeyboardButton(text='Установить время'))
    bot.send_message(message.from_user.id, 'Возможные действия', reply_markup=keyboard)
