import threading

import telebot

from authentication import start_auth
from bot_data import genres, movie_data_imdb, music_data_spotify
from main_buttons import create_buttons
from remind import start_check_reminders, process_reminder_time
from bot_data import bot
from search_recommend import (create_keyboard, callback_music, send_slider,
                              callback, create_inline_keyboard, callback_movie_count,
                              callback_movie_genre, handle_query, callback_movie_rate, callback_movie_title)
from selection_top import (create_inline_keyboard_spotify_genre, send_music, create_inline_keyboard_spot,
                           callback_kinopoisk, send_movie,
                           create_inline_keyboard_imdb_genre, callback_spotify, callback_imdb,
                           create_inline_keyboard_movie)


# engine = create_engine('postgresql://postgres:postgres@localhost:5432/media-fusion')
# Session = sessionmaker(bind=engine)


@bot.message_handler(commands=['start'])
def start(message):
    start_auth(message)


@bot.message_handler(func=lambda message: message.text == 'Установить время')
def process_keyboard_(message):
    bot.send_message(message.from_user.id, 'Введите время напоминания в формате HH:MM (например, 09:00):')
    bot.register_next_step_handler(message, process_reminder_time)


@bot.message_handler(func=lambda message: message.text == 'Подборка топа')
def process_keyboard_(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
    keyboard.add(telebot.types.KeyboardButton(text='Топ 10 kinopoisk'),
                 telebot.types.KeyboardButton(text='Топ 10 imdb'),
                 telebot.types.KeyboardButton(text='Топ 10 spotify'),
                 telebot.types.KeyboardButton(text='Назад'))
    bot.send_message(message.from_user.id, 'Возможные действия', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Топ 10 spotify')
def process_keyboard_(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
    keyboard.add(telebot.types.KeyboardButton(text='Топ 10 spotify по жанрам'),
                 telebot.types.KeyboardButton(text='Топ 10 spotify по исполнителям'),
                 telebot.types.KeyboardButton(text='Назад'))
    bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Топ 10 spotify по жанрам')
def process_keyboard_(message):
    bot.send_message(message.chat.id, f'Выберите один жанр из списка:',
                     reply_markup=create_inline_keyboard_spotify_genre())


@bot.callback_query_handler(func=lambda call: call.data.endswith('_tops'))
def callback_handler(call):
    filtered_music = [song for song in music_data_spotify if call.data[:-5] == song['track_genre']]
    send_music(filtered_music, call)


@bot.message_handler(func=lambda message: message.text == 'Топ 10 spotify по исполнителям')
def process_keyboard_(message):
    bot.send_message(message.from_user.id, 'Выберите исполнителя', reply_markup=create_inline_keyboard_spot(1))


@bot.callback_query_handler(func=lambda call: call.data.startswith('spot_artist') or call.data.startswith(
    'prev_page_spot') or call.data.startswith('next_page_spot'))
def callback_handler(call):
    callback_spotify(call)


@bot.message_handler(func=lambda message: message.text == 'Топ 10 kinopoisk')
def process_keyboard_(message):
    bot.send_message(message.from_user.id, 'Выберите год',
                     reply_markup=create_inline_keyboard_movie(7, [i for i in range(1921, 2020)] + [None]))


@bot.callback_query_handler(func=lambda call: call.data.startswith('kino_years') or call.data.startswith(
    'prev_page_kino') or call.data.startswith('next_page_kino'))
def callback_handler(call):
    callback_kinopoisk(call)


@bot.message_handler(func=lambda message: message.text == 'Топ 10 imdb')
def process_keyboard_(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
    keyboard.add(telebot.types.KeyboardButton(text='Топ 10 imdb по году'),
                 telebot.types.KeyboardButton(text='Топ 10 imdb по жанрам'),
                 telebot.types.KeyboardButton(text='Назад'))
    bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Топ 10 imdb по году')
def process_keyboard_(message):
    bot.send_message(message.from_user.id, 'Выберите год',
                     reply_markup=create_inline_keyboard_movie(7, [i for i in range(1916, 2017)] + [None]))


@bot.callback_query_handler(func=lambda call: call.data.startswith('imdb_years') or call.data.startswith(
    'prev_page_imdb') or call.data.startswith('next_page_imdb'))
def callback_handler(call):
    callback_imdb(call)


@bot.message_handler(func=lambda message: message.text == 'Топ 10 imdb по жанрам')
def process_keyboard_(message):
    bot.send_message(message.chat.id, f'Выберите один жанр из списка:',
                     reply_markup=create_inline_keyboard_imdb_genre())


@bot.callback_query_handler(func=lambda call: call.data.endswith('_top'))
def callback_handler(call):
    filtered_movies = [movie for movie in movie_data_imdb if call.data[:-4] in movie['genres']]
    send_movie(call, filtered_movies)


@bot.message_handler(func=lambda message: message.text == 'Назад')
def process_keyboard(message):
    create_buttons(message)


@bot.message_handler(func=lambda message: message.text == 'Поиск рекомендованной музыки')
def process_keyboard(message):
    bot.send_message(message.from_user.id, 'Выберите трек для поиска похожих:',
                     reply_markup=create_keyboard(1, 'music'))


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('music_') or call.data.startswith('prev_page_music') or call.data.startswith(
        'next_page_music'))
def callback_handler(call):
    callback(call, 'music', 'm')


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('movie_') or call.data.startswith('prev_page_movie') or call.data.startswith(
        'next_page_movie'))
def callback_handler(call):
    callback(call, 'movie', 't')


@bot.callback_query_handler(func=lambda call: call.data.startswith('sliderm_') or call.data.startswith(
    'forwardm_') or call.data.startswith('backwardm_'))
def callback_handler(call):
    callback_music(call)


@bot.inline_handler(lambda query: query.query.startswith('music: '))
def handle_inline_query(query):
    handle_query(query, 'music', 'm')


@bot.inline_handler(lambda query: query.query.startswith('movie: '))
def handle_inline_query(query):
    handle_query(query, 'movie', '')


@bot.callback_query_handler(func=lambda call: call.data.startswith('countm_') or call.data.startswith('count_'))
def callback_handler(call):
    title = call.data.split('_')[-1]
    type = call.data.split('_')[0][-1]
    send_slider(call.from_user.id, type,
                'Нажмите на стрелочки для изменения кол-ва\nНажмите на число для выбора',
                4, title)


@bot.message_handler(func=lambda message: message.text == 'Поиск рекомендованных фильмов')
def process_keyboard(message):
    bot.send_message(message.from_user.id, 'Выберите способ поиска похожих фильмов:',
                     reply_markup=create_inline_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == 'search_by_genre')
def process_search_by_genre(call):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttons = [telebot.types.InlineKeyboardButton(genre, callback_data=genre) for genre in genres]
    keyboard.add(*buttons)
    keyboard.add(telebot.types.InlineKeyboardButton("Готово", callback_data="done"))
    bot.send_message(call.message.chat.id,
                     f'Выберите один или несколько жанров из списка и нажмите "Готово" после выбора:',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'search_by_title')
def process_search_by_title(call):
    user_id = call.message.chat.id
    bot.send_message(user_id, 'Выберите фильм для поиска\nрекомендаций на его основе:',
                     reply_markup=create_keyboard(1, 'movie'))


@bot.callback_query_handler(func=lambda call: call.data.startswith('sliderc_') or call.data.startswith(
    'forwardc_') or call.data.startswith('backwardc'))
def callback_handler(call):
    callback_movie_count(call)


@bot.callback_query_handler(func=lambda call: call.data in genres or call.data == 'done')
def callback_handler(call):
    callback_movie_genre(call)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('slider_') or call.data.startswith('forward_') or call.data.startswith(
        'backward_'))
def callback_handler(call):
    callback_movie_rate(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('slidert_') or call.data.startswith(
    'forwardt_') or call.data.startswith('backwardt_'))
def callback_handler(call):
    callback_movie_title(call)


def main():
    reminder_thread = threading.Thread(target=start_check_reminders)
    reminder_thread.start()
    bot.polling()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        main()
