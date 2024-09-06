import threading

import telebot

from authentication import start_auth
from bot_data import data_music, tracks, data, songs, movies, genres, movie_data_imdb, movie_data_kinopoisk, \
    music_data_spotify, spotify_artist, spotify_genre
from main_buttons import create_buttons
from parser_info import parse_website_film, parse_video_link
from recommendation import music_recommendation, movie_recommender
from remind import start_check_reminders, process_reminder_time
from bot_data import bot
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
                     reply_markup=create_inline_keyboard_music(1))


def create_inline_keyboard_music(page):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    start_index = (page - 1) * 5
    end_index = min(start_index + 5, len(tracks))
    for i in range(start_index, end_index):
        keyboard.add(telebot.types.InlineKeyboardButton(f'Author: {tracks[i][0]}     track: {tracks[i][1]}',
                                                        callback_data=f'music_{i}'))
    if page > 1:
        keyboard.add(telebot.types.InlineKeyboardButton('◀ Предыдущая', callback_data=f'prev_page_music_{page}'))
    if end_index < len(tracks):
        keyboard.add(telebot.types.InlineKeyboardButton('Следующая ▶', callback_data=f'next_page_music_{page}'))
    keyboard.add(telebot.types.InlineKeyboardButton('Начать поиск трека', switch_inline_query_current_chat='music: '))
    return keyboard


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('music_') or call.data.startswith('prev_page_music') or call.data.startswith(
        'next_page_music'))
def callback_handler(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data.startswith('music_'):
        page = int(call.data.split('_')[-1]) // 5
    else:
        page = int(call.data.split('_')[-1])

    if call.data.startswith('prev_page_music'):
        page -= 1
    elif call.data.startswith('next_page_music'):
        page += 1
    else:
        music_index = int(call.data.split('_')[-1])
        send_slider_music(user_id, 4, f'{tracks[music_index][0]}*{tracks[music_index][1]}')
        return

    keyboard = create_inline_keyboard_music(page)
    bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('slider_music_') or call.data.startswith(
    'forwardm_') or call.data.startswith('backwardm_'))
def callback_handler(call):
    title = call.data.split('_')[-2]
    if call.data.startswith('forwardm_') or call.data.startswith('backwardm_'):

        current_value = int(call.data.split('_')[-1])

        if call.data.startswith('forwardm_'):
            if current_value != 10:
                current_value = min(current_value + 1, 10)
                edit_slider_music(call, current_value, title)
        elif call.data.startswith('backwardm_'):
            if current_value != 1:
                current_value = max(current_value - 1, 1)
                edit_slider_music(call, current_value, title)
    if call.data.startswith('slider_music_'):
        value = int(call.data.split('_')[-1])
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Вы выбрали {value} похожих композиций на {' '.join(title.split('*'))}',
                              reply_markup=None)
        show_music_title(call.message, value, title)


def send_slider_music(user_id, value, title):
    bot.send_message(user_id, 'Нажмите на стрелочки для изменения кол-ва музыки\nНажмите на число для выбора',
                     reply_markup=create_slider_keyboard_music(value, title))


def edit_slider_music(call, value, title):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=create_slider_keyboard_music(value, title))


def create_slider_keyboard_music(value, title):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    backward_button = telebot.types.InlineKeyboardButton('◀', callback_data=f'backwardm_{title}_{value}')
    forward_button = telebot.types.InlineKeyboardButton('▶', callback_data=f'forwardm_{title}_{value}')
    value_button = telebot.types.InlineKeyboardButton(str(value), callback_data=f'slider_music_{title}_{value}')
    keyboard.add(backward_button, value_button, forward_button)
    return keyboard


@bot.inline_handler(lambda query: query.query.startswith('music: '))
def handle_inline_query(query):
    results = []
    max_results = 10
    for value in tracks:
        if query.query.lower()[8:] in f'{value[0]} {value[1]}'.lower():
            results.append(telebot.types.InlineQueryResultArticle(
                id=str(len(results)),
                title=f'{value[0]} - {value[1]}',
                input_message_content=telebot.types.InputTextMessageContent(
                    message_text=f'Поиск похожих фильмов по {f'{value[0]} - {value[1]}'}\nВыберите количество'),
                reply_markup=create_slider_keyboard_query_music(f'{value[0]}*{value[1]}')
            ))
            if len(results) >= max_results:
                break
    bot.answer_inline_query(query.id, results)


def create_slider_keyboard_query_music(title):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    button = telebot.types.InlineKeyboardButton('Перейти к выбору количества предложенных треков',
                                                callback_data=f'countm_{title}')
    keyboard.add(button)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith('countm_'))
def callback_handler(call):
    title = call.data.split('_')[-1]
    send_slider_music(call.from_user.id, 4, title)


@bot.message_handler(func=lambda message: message.text == 'Поиск рекомендованных фильмов')
def process_keyboard(message):
    bot.send_message(message.from_user.id, 'Выберите способ поиска похожих фильмов:',
                     reply_markup=create_inline_keyboard())


def create_inline_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_genre = telebot.types.InlineKeyboardButton(text='По жанру', callback_data='search_by_genre')
    button_title = telebot.types.InlineKeyboardButton(text='По названию', callback_data='search_by_title')
    keyboard.add(button_genre, button_title)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data == 'search_by_genre')
def process_search_by_genre(call):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttons = [telebot.types.InlineKeyboardButton(genre, callback_data=genre) for genre in genres]
    keyboard.add(*buttons)
    keyboard.add(telebot.types.InlineKeyboardButton("Готово", callback_data="done"))
    bot.send_message(call.message.chat.id,
                     f'Выберите один или несколько жанров из списка и нажмите "Готово" после выбора:',
                     reply_markup=keyboard)


def process_genre_count(message, genre, rate, count):
    try:
        count = int(count)
        if count <= 0:
            bot.send_message(message.chat.id, 'Введите положительное число больше нуля:')
            bot.register_next_step_handler(message, process_genre_count)
        else:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id,
                             f'Вы выбрали поиск похожих по жанру "{genre}" и рейтингу {rate}. Количество фильмов: {count}')
            show_films_genre(message, count, genre, rate)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите корректное число:')
        bot.register_next_step_handler(message, process_genre_count)


def process_count(message, genre, rate):
    user_id = message.chat.id
    send_slider_count(user_id, 3, genre, rate)


def send_slider_count(user_id, value, genre, rate):
    bot.send_message(user_id, 'Нажмите на стрелочки для изменения выбора\nчисла фильмов\nНажмите на число для выбора',
                     reply_markup=create_slider_keyboard_count(value, genre, rate))


def edit_slider_count(call, value, genre, rate):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=create_slider_keyboard_count(value, genre, rate))


def create_slider_keyboard_count(value, genre, rate):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    backward_button = telebot.types.InlineKeyboardButton('◀', callback_data=f'count_backward_{genre}_{rate}_{value}')
    forward_button = telebot.types.InlineKeyboardButton('▶', callback_data=f'count_forward_{genre}_{rate}_{value}')
    value_button = telebot.types.InlineKeyboardButton(str(value),
                                                      callback_data=f'count_slider_value_{genre}_{rate}_{value}')
    keyboard.add(backward_button, value_button, forward_button)
    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith('count_slider_value_') or call.data.startswith(
    'count_forward_') or call.data.startswith('count_backward_'))
def callback_handler(call):
    genre = call.data.split('_')[-3]
    rate = call.data.split('_')[-2]
    if call.data.startswith('count_forward_') or call.data.startswith('count_backward_'):

        current_value = int(call.data.split('_')[-1])

        if call.data.startswith('count_forward_'):
            if current_value != 15:
                current_value = min(current_value + 1, 15)
                edit_slider_count(call, current_value, genre, rate)
        elif call.data.startswith('count_backward_'):
            if current_value != 1:
                current_value = max(current_value - 1, 1)
                edit_slider_count(call, current_value, genre, rate)
    if call.data.startswith('count_slider_value_'):
        count = call.message.json['reply_markup']['inline_keyboard'][0][1]['text']
        process_genre_count(call.message, genre, rate, count)


@bot.callback_query_handler(func=lambda call: call.data in genres or call.data == 'done')
def callback_handler(call):
    if call.message.text:
        current_genres = call.message.text.split(
            'Выберите один или несколько жанров из списка и нажмите "Готово" после выбора:'
        )[1].strip().split(', ')
        if current_genres[0] == '':
            current_genres = []
    else:
        current_genres = []

    if call.data == "done" and current_genres != []:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Выбранные жанры: {", ".join(current_genres)}', reply_markup=None)
        process_rate(call.message, ', '.join(current_genres))
        return
    elif call.data == "done":
        return

    selected_genre = call.data

    if selected_genre in current_genres:
        current_genres.remove(selected_genre)
    else:
        current_genres.append(selected_genre)

    new_message_text = 'Выберите один или несколько жанров из списка и нажмите "Готово" после выбора:\n' + ', '.join(
        current_genres)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=new_message_text, reply_markup=call.message.reply_markup)


def process_rate(message, genre):
    user_id = message.chat.id
    send_slider(user_id, 8, genre)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('slider_value_') or call.data.startswith('forward_') or call.data.startswith(
        'backward_'))
def callback_handler(call):
    genre = call.data.split('_')[-2]
    if call.data.startswith('forward_') or call.data.startswith('backward_'):

        current_value = int(call.data.split('_')[-1])

        if call.data.startswith('forward_'):
            if current_value != 10:
                current_value = min(current_value + 1, 10)
                edit_slider(call, current_value, genre)
        elif call.data.startswith('backward_'):
            if current_value != 1:
                current_value = max(current_value - 1, 1)
                edit_slider(call, current_value, genre)
    if call.data.startswith('slider_value_'):
        rate = call.message.json['reply_markup']['inline_keyboard'][0][1]['text']
        process_genre_rate(call.message, genre, rate)


def send_slider(user_id, value, genre):
    bot.send_message(user_id, 'Нажмите на стрелочки для изменения рейтинга\nНажмите на число для выбора',
                     reply_markup=create_slider_keyboard(value, genre))


def edit_slider(call, value, genre):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, reply_markup=create_slider_keyboard(value, genre))


def create_slider_keyboard(value, genre):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    backward_button = telebot.types.InlineKeyboardButton('◀', callback_data=f'backward_{genre}_{value}')
    forward_button = telebot.types.InlineKeyboardButton('▶', callback_data=f'forward_{genre}_{value}')
    value_button = telebot.types.InlineKeyboardButton(str(value), callback_data=f'slider_value_{genre}_{value}')
    keyboard.add(backward_button, value_button, forward_button)
    return keyboard


def process_genre_rate(message, genre, rate):
    try:
        rate = int(rate)
        if rate <= 0 or rate > 10:
            bot.send_message(message.chat.id, 'Введите корректное число: от 1 до 10')
            bot.register_next_step_handler(message, process_genre_rate, genre)
        else:
            bot.delete_message(message.chat.id, message.message_id)
            process_count(message, genre, rate)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите корректное число:')
        bot.register_next_step_handler(message, process_genre_rate, genre)


def show_films_genre(message, count, sel_gen, rate):
    test_point = [1 if genre in sel_gen.split(', ') else 0 for genre in genres]
    test_point.append(int(rate))
    table = movie_recommender(test_point, int(count))

    ind = 0
    for movie, link, ratings in table:
        ind += 1
        bot.send_message(message.chat.id, f'{ind}. Фильм - {movie}.\n'
                                          f'IMDB Rating: {ratings}⭐\n'
                                          f'link - {link}')
        movie_info = parse_website_film(link)
        el = parse_video_link(link)
        if el is not None:
            bot.send_message(message.chat.id, f'Trailer:\n{el}')
        if movie_info:
            bot.send_message(message.chat.id, f'{movie_info[0]}\n'
                                              f'{movie_info[1]}\n'
                                              f'{movie_info[2]}\n')

        else:
            bot.send_message(message.chat.id, 'Не удалось получить информацию о фильме')


@bot.callback_query_handler(func=lambda call: call.data == 'search_by_title')
def process_search_by_title(call):
    send_first_page(call.message)


def process_title_count(message):
    try:
        count = int(message.text)
        if count <= 0:
            bot.send_message(message.chat.id, 'Введите положительное число больше нуля:')
            bot.register_next_step_handler(message, process_title_count)
        else:
            send_first_page(message)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите корректное число:')
        bot.register_next_step_handler(message, process_genre_count)


def process_title(message, count):
    title = message.text
    if title not in movies:
        bot.send_message(message.chat.id, 'Выберите другой фильм:')
        bot.register_next_step_handler(message, process_title, count)
    else:
        bot.send_message(message.chat.id, f'Вы выбрали поиск по названию "{title}". Количество фильмов: {count}')
        show_films_title(message, count, title)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('movie_') or call.data.startswith('prev_page') or call.data.startswith(
        'next_page'))
def callback_handler(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data.startswith('movie_'):
        page = int(call.data.split('_')[-1]) // 5
    else:
        page = int(call.data.split('_')[-1])

    if call.data.startswith('prev_page'):
        page -= 1
    elif call.data.startswith('next_page'):
        page += 1
    else:
        movie_index = int(call.data.split('_')[-1])
        send_slider_title(user_id, 4, movies[movie_index])
        return

    keyboard = create_movies_keyboard(movies, page)
    bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('count_'))
def callback_handler(call):
    title = call.data.split('_')[-1]
    send_slider_title(call.from_user.id, 4, title)


def create_movies_keyboard(movies, page):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    start_index = (page - 1) * 5
    end_index = min(start_index + 5, len(movies))
    for i in range(start_index, end_index):
        keyboard.add(telebot.types.InlineKeyboardButton(movies[i], callback_data=f'movie_{i}'))
    if page > 1:
        keyboard.add(telebot.types.InlineKeyboardButton('◀ Предыдущая', callback_data=f'prev_page_{page}'))
    if end_index < len(movies):
        keyboard.add(telebot.types.InlineKeyboardButton('Следующая ▶', callback_data=f'next_page_{page}'))
    keyboard.add(telebot.types.InlineKeyboardButton('Начать поиск фильма', switch_inline_query_current_chat='movies: '))
    return keyboard


def send_first_page(message):
    user_id = message.chat.id
    bot.send_message(user_id, 'Выберите фильм для поиска\nрекомендаций на его основе:',
                     reply_markup=create_movies_keyboard(movies, 1))


@bot.inline_handler(lambda query: query.query.startswith('movies: '))
def handle_inline_query(query):
    results = []
    max_results = 10
    for movie in movies:
        if query.query.lower()[8:] in movie.lower():
            results.append(telebot.types.InlineQueryResultArticle(
                id=str(len(results)),
                title=movie,
                input_message_content=telebot.types.InputTextMessageContent(
                    message_text=f'Поиск похожих фильмов по {movie}\nВыберите количество'),
                reply_markup=create_slider_keyboard_query(movie)
            ))
            if len(results) >= max_results:
                break
    bot.answer_inline_query(query.id, results)


@bot.callback_query_handler(func=lambda call: call.data.startswith('slider_title_') or call.data.startswith(
    'forwardt_') or call.data.startswith('backwardt_'))
def callback_handler(call):
    title = call.data.split('_')[-2]
    if call.data.startswith('forwardt_') or call.data.startswith('backwardt_'):

        current_value = int(call.data.split('_')[-1])

        if call.data.startswith('forwardt_'):
            if current_value != 10:
                current_value = min(current_value + 1, 10)
                edit_slider_title(call, current_value, title)
        elif call.data.startswith('backwardt_'):
            if current_value != 1:
                current_value = max(current_value - 1, 1)
                edit_slider_title(call, current_value, title)
    if call.data.startswith('slider_title_'):
        value = int(call.data.split('_')[-1])
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Вы выбрали {value} похожих фильмов на {title}', reply_markup=None)
        show_films_title(call.message, value, title)


def send_slider_title(user_id, value, title):
    bot.send_message(user_id, 'Нажмите на стрелочки для изменения кол-ва фильмов\nНажмите на число для выбора',
                     reply_markup=create_slider_keyboard_title(value, title))


def edit_slider_title(call, value, title):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=create_slider_keyboard_title(value, title))


def create_slider_keyboard_title(value, title):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    backward_button = telebot.types.InlineKeyboardButton('◀', callback_data=f'backwardt_{title}_{value}')
    forward_button = telebot.types.InlineKeyboardButton('▶', callback_data=f'forwardt_{title}_{value}')
    value_button = telebot.types.InlineKeyboardButton(str(value), callback_data=f'slider_title_{title}_{value}')
    keyboard.add(backward_button, value_button, forward_button)
    return keyboard


def create_slider_keyboard_query(title):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    button = telebot.types.InlineKeyboardButton('Перейти к выбору количества предложенных фильмов',
                                                callback_data=f'count_{title}')
    keyboard.add(button)
    return keyboard


def show_films_title(message, count, title):
    test_points = data[movies.index(title)]
    table = movie_recommender(test_points, count + 1)
    table.pop(0)
    ind = 0
    for movie, link, ratings in table:
        ind += 1
        bot.send_message(message.chat.id, f'{ind}. Фильм - {movie}.\n'
                                          f'IMDB Rating: {ratings}⭐\n'
                                          f'link - {link}')
        movie_info = parse_website_film(link)
        el = parse_video_link(link)
        if el is not None:
            bot.send_message(message.chat.id, f'Trailer:\n{el}')
        if movie_info:
            bot.send_message(message.chat.id, f'{movie_info[0]}\n'
                                              f'{movie_info[1]}\n'
                                              f'{movie_info[2]}\n')

        else:
            bot.send_message(message.chat.id, 'Не удалось получить информацию о фильме')


def show_music_title(message, count, title: str):
    test_points = data_music[songs.index(tuple(title.split('*')))]
    table = music_recommendation(test_points, count + 1)
    table.pop(0)
    for ind, value in enumerate(table, start=1):
        bot.send_message(message.chat.id, f'{ind})Author: {value[0]}\n'
                                          f'track: {value[1]}\n'
                                          f'Year: {value[2]}\n'
                                          f'Genre: {value[3]}')


def main():
    reminder_thread = threading.Thread(target=start_check_reminders)
    reminder_thread.start()
    bot.polling()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        main()
