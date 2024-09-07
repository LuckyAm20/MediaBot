import telebot

from bot_data import movies, tracks, bot, data_music, songs, data, genres
from parser_info import parse_video_link, parse_website_film
from recommendation import music_recommendation, movie_recommender


def create_keyboard(page, name):
    items = tracks if name == 'music' else movies

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    start_index = (page - 1) * 5
    end_index = min(start_index + 5, len(items))
    for i in range(start_index, end_index):
        text = f'Author: {items[i][0]}     track: {items[i][1]}' if name == 'music' else items[i]
        keyboard.add(telebot.types.InlineKeyboardButton(text, callback_data=f'{name}_{i}'))
    if page > 1:
        keyboard.add(telebot.types.InlineKeyboardButton('◀ Предыдущая', callback_data=f'prev_page_{name}_{page}'))
    if end_index < len(items):
        keyboard.add(telebot.types.InlineKeyboardButton('Следующая ▶', callback_data=f'next_page_{name}_{page}'))
    keyboard.add(telebot.types.InlineKeyboardButton(f'Начать поиск {name}',
                                                    switch_inline_query_current_chat=f'{name}: '))
    return keyboard


def callback(call, name, type):
    user_id = call.message.chat.id
    message_id = call.message.message_id
    if call.data.startswith(f'{name}_'):
        page = int(call.data.split('_')[-1]) // 5
    else:
        page = int(call.data.split('_')[-1])

    if call.data.startswith(f'prev_page_{name}'):
        page -= 1
    elif call.data.startswith(f'next_page_{name}'):
        page += 1
    else:
        index = int(call.data.split('_')[-1])
        items = movies[index] if name == 'movie' else f'{tracks[index][0]}*{tracks[index][1]}'
        send_slider(user_id, type,
                    'Нажмите на стрелочки для изменения кол-ва \nНажмите на число для выбора',
                    4, items)
        return

    keyboard = create_keyboard(page, name)
    bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=keyboard)


def callback_music(call):
    title = call.data.split('_')[-2]
    if call.data.startswith('forwardm_') or call.data.startswith('backwardm_'):

        current_value = int(call.data.split('_')[-1])

        if call.data.startswith('forwardm_'):
            if current_value != 10:
                current_value = min(current_value + 1, 10)
                edit_slider(call, 'm', current_value, title)
        elif call.data.startswith('backwardm_'):
            if current_value != 1:
                current_value = max(current_value - 1, 1)
                edit_slider(call, 'm', current_value, title)
    if call.data.startswith('sliderm_'):
        value = int(call.data.split('_')[-1])
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Вы выбрали {value} похожих композиций на {' '.join(title.split('*'))}',
                              reply_markup=None)
        show_music_title(call.message, value, title)


def send_slider(user_id, type, text, value, genre, rate=None):
    bot.send_message(user_id, text,
                     reply_markup=create_slider_keyboard(type, value, genre, rate))


def edit_slider(call, type, value, genre, rate=None):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=create_slider_keyboard(type, value, genre, rate))


def create_slider_keyboard(type, value, genre, rate=None):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    if rate is None:
        text = f'{genre}_{value}'
    else:
        text = f'{genre}_{rate}_{value}'
    backward_button = telebot.types.InlineKeyboardButton('◀', callback_data=f'backward{type}_{text}')
    forward_button = telebot.types.InlineKeyboardButton('▶', callback_data=f'forward{type}_{text}')
    value_button = telebot.types.InlineKeyboardButton(str(value),
                                                      callback_data=f'slider{type}_{text}')
    keyboard.add(backward_button, value_button, forward_button)
    return keyboard


def handle_query(query, name, type):
    results = []
    max_results = 10
    items = movies if name == 'movie' else tracks
    for value in items:
        if name == 'movie':
            element = title = el = value
        else:
            element = f'{value[0]} {value[1]}'
            title = f'{value[0]} - {value[1]}'
            el = f'{value[0]}*{value[1]}'
        if query.query.lower()[8:] in element.lower():
            results.append(telebot.types.InlineQueryResultArticle(
                id=str(len(results)),
                title=title,
                input_message_content=telebot.types.InputTextMessageContent(
                    message_text=f'Поиск похожих {name} по {element}\nВыберите количество'),
                reply_markup=create_slider_keyboard_query(el, type, name)
            ))
            if len(results) >= max_results:
                break
    bot.answer_inline_query(query.id, results)


def create_slider_keyboard_query(title, type, name):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    button = telebot.types.InlineKeyboardButton(f'Перейти к выбору количества предложенных {name}',
                                                callback_data=f'count{type}_{title}')
    keyboard.add(button)
    return keyboard


def create_inline_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_genre = telebot.types.InlineKeyboardButton(text='По жанру', callback_data='search_by_genre')
    button_title = telebot.types.InlineKeyboardButton(text='По названию', callback_data='search_by_title')
    keyboard.add(button_genre, button_title)
    return keyboard


def callback_movie_count(call):
    genre = call.data.split('_')[-3]
    rate = call.data.split('_')[-2]
    if call.data.startswith('forwardc_') or call.data.startswith('backwardc_'):

        current_value = int(call.data.split('_')[-1])

        if call.data.startswith('forwardc_'):
            if current_value != 15:
                current_value = min(current_value + 1, 15)
                edit_slider(call, 'c', current_value, genre, rate)
        elif call.data.startswith('backwardc_'):
            if current_value != 1:
                current_value = max(current_value - 1, 1)
                edit_slider(call, 'c', current_value, genre, rate)
    if call.data.startswith('sliderc_'):
        count = call.message.json['reply_markup']['inline_keyboard'][0][1]['text']
        bot.send_message(call.message.chat.id,
                         f'Вы выбрали поиск похожих по жанру "{genre}" и рейтингу {rate}. Количество фильмов: {count}')
        show_films_genre(call.message, count, genre, rate)


def callback_movie_rate(call):
    genre = call.data.split('_')[-2]
    if call.data.startswith('forward_') or call.data.startswith('backward_'):

        current_value = int(call.data.split('_')[-1])

        if call.data.startswith('forward_'):
            if current_value != 10:
                current_value = min(current_value + 1, 10)
                edit_slider(call, '', current_value, genre)
        elif call.data.startswith('backward_'):
            if current_value != 1:
                current_value = max(current_value - 1, 1)
                edit_slider(call, '', current_value, genre)
    if call.data.startswith('slider_'):
        rate = call.message.json['reply_markup']['inline_keyboard'][0][1]['text']

        send_slider(call.message.chat.id, 'c',
                    'Нажмите на стрелочки для изменения выбора\nчисла фильмов\nНажмите на число для выбора',
                    3, genre, rate)


def callback_movie_title(call):
    title = call.data.split('_')[-2]
    if call.data.startswith('forwardt_') or call.data.startswith('backwardt_'):

        current_value = int(call.data.split('_')[-1])

        if call.data.startswith('forwardt_'):
            if current_value != 10:
                current_value = min(current_value + 1, 10)
                edit_slider(call, 't', current_value, title)
        elif call.data.startswith('backwardt_'):
            if current_value != 1:
                current_value = max(current_value - 1, 1)
                edit_slider(call, 't', current_value, title)
    if call.data.startswith('slidert_'):
        value = int(call.data.split('_')[-1])
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Вы выбрали {value} похожих фильмов на {title}', reply_markup=None)
        show_films_title(call.message, value, title)


def callback_movie():
    ...


def callback_movie_genre(call):
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
        send_slider(call.message.chat.id, '',
                    'Нажмите на стрелочки для изменения рейтинга\nНажмите на число для выбора',
                    8, ', '.join(current_genres))
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


def show_films_genre(message, count, sel_gen, rate):
    test_point = [1 if genre in sel_gen.split(', ') else 0 for genre in genres]
    test_point.append(int(rate))
    table = movie_recommender(test_point, int(count))

    film_info(message, table)


def show_films_title(message, count, title):
    test_points = data[movies.index(title)]
    table = movie_recommender(test_points, count + 1)
    table.pop(0)
    film_info(message, table)


def film_info(message, table):
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
