import telebot

from bot_data import (spotify_genre, bot_tg, spotify_artist, music_data_spotify,
                      movie_data_kinopoisk, genres, movie_data_imdb)


def create_inline_keyboard_spotify_genre():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    buttons = [telebot.types.InlineKeyboardButton(genre, callback_data=f'{genre}_tops') for genre in spotify_genre]
    keyboard.add(*buttons)
    return keyboard


def send_music(music, call):
    sorted_music = sorted(music, key=lambda x: x['popularity'], reverse=True)[:10]
    for ind, track in enumerate(sorted_music, start=1):
        bot_tg.send_message(call.message.chat.id, f'{ind}) {track['artists']} - {track['track_name']}\n'
                                                  f'Genre: {track['track_genre']}\n'
                                                  f'Popularity: {track['popularity']}')


def create_inline_keyboard_spot(page):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    name = spotify_artist + [None]
    start_index = (page - 1) * 20
    end_index = min(start_index + 20, len(name))
    for i in range(start_index, end_index):
        keyboard.add(telebot.types.InlineKeyboardButton(f'{name[i] if name[i] is not None else "все исполнители"}',
                                                        callback_data=f'spot_artist_{name[i]}'))
    if page > 1:
        keyboard.add(telebot.types.InlineKeyboardButton('◀ Предыдущая', callback_data=f'prev_page_spot_{page}'))
    if end_index < len(name):
        keyboard.add(telebot.types.InlineKeyboardButton('Следующая ▶', callback_data=f'next_page_spot_{page}'))
    return keyboard


def callback_spotify(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    page = 1
    if not call.data.startswith('spot_artist'):
        page = int(call.data.split('_')[-1])

    if call.data.startswith('prev_page_spot'):
        page -= 1
    elif call.data.startswith('next_page_spot'):
        page += 1
    else:
        index = call.data.split('_')[-1]
        if index != 'None':
            filtered_music = [song for song in music_data_spotify if index == song['artists']]
        else:
            filtered_music = music_data_spotify

        send_music(filtered_music, call)
        return

    keyboard = create_inline_keyboard_spot(page)
    bot_tg.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=keyboard)


def create_inline_keyboard_movie(page, years):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    start_index = (page - 1) * 15
    end_index = min(start_index + 15, len(years))
    for i in range(start_index, end_index):
        keyboard.add(telebot.types.InlineKeyboardButton(f'{years[i] if years[i] is not None else "все время"}',
                                                        callback_data=f'kino_years_{years[i]}'))
    if page > 1:
        keyboard.add(telebot.types.InlineKeyboardButton('◀ Предыдущая', callback_data=f'prev_page_kino_{page}'))
    if end_index < len(years):
        keyboard.add(telebot.types.InlineKeyboardButton('Следующая ▶', callback_data=f'next_page_kino_{page}'))
    return keyboard


def callback_kinopoisk(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    page = 1
    if not call.data.startswith('kino_years'):
        page = int(call.data.split('_')[-1])

    if call.data.startswith('prev_page_kino'):
        page -= 1
    elif call.data.startswith('next_page_kino'):
        page += 1
    else:
        index = call.data.split('_')[-1]
        if index != 'None':
            filtered_movies = [movie for movie in movie_data_kinopoisk if int(movie['year']) == int(index)]
        else:
            filtered_movies = movie_data_kinopoisk
        sorted_movies = sorted(filtered_movies, key=lambda x: x['rating_ball'], reverse=True)[:10]

        for ind, movie in enumerate(sorted_movies, start=1):
            bot_tg.send_message(call.message.chat.id, f'{ind})Film: {movie['movie']}\n'
                                                      f'Year: {movie['year']}\n'
                                                      f'Country: {movie['country']}\n'
                                                      f'Rating: {movie['rating_ball']}\n'
                                                      f'Description: {movie['overview']}\n'
                                                      f'Logo URL:\n{movie['url_logo'][1:-1]}')
        return

    keyboard = create_inline_keyboard_movie(page, [i for i in range(1921, 2020)] + [None])
    bot_tg.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=keyboard)


def callback_imdb(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    page = 1
    if not call.data.startswith('imdb_years'):
        page = int(call.data.split('_')[-1])

    if call.data.startswith('prev_page_imdb'):
        page -= 1
    elif call.data.startswith('next_page_imdb'):
        page += 1
    else:
        index = call.data.split('_')[-1]
        if index != 'None':
            filtered_movies = [movie for movie in movie_data_imdb if movie['title_year'] == int(index)]
        else:
            filtered_movies = movie_data_imdb

        send_movie(call, filtered_movies)

        return

    keyboard = create_inline_keyboard_movie(page, [i for i in range(1916, 2017)] + [None])
    bot_tg.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=keyboard)


def create_inline_keyboard_imdb_genre():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttons = [telebot.types.InlineKeyboardButton(genre, callback_data=f'{genre}_top') for genre in genres]
    keyboard.add(*buttons)
    return keyboard


def send_movie(call, filtered_movies):
    sorted_movies = sorted(filtered_movies, key=lambda x: x['imdb_score'], reverse=True)[:10]

    for ind, movie in enumerate(sorted_movies, start=1):
        bot_tg.send_message(call.message.chat.id, f'{ind})Film: {movie['movie_title']}\n'
                                                  f'Genres: {movie['genres']}\n'
                                                  f'Country: {movie['country']}\n'
                                                  f'Year: {movie['title_year']}\n'
                                                  f'Rating: {movie['imdb_score']}\n'
                                                  f'IMDB link: {movie['movie_imdb_link']}')
