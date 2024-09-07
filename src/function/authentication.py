import hashlib
import re

from bot_data import bot_tg
from database.database import User, Session
from main_buttons import create_buttons


def start_auth(message):
    user = message.from_user
    if user.username is None:
        bot_tg.send_message(user.id, 'Для использования бота, пожалуйста, установите username в настройках Telegram.')
        bot_tg.send_message(user.id, 'Как только вы установите username, напишите любое сообщение для продолжения.')
        bot_tg.register_next_step_handler(message, check_username_set, bot_tg)
    else:
        authenticate(message)


def authenticate(message):
    bot_tg.send_message(message.from_user.id, 'Введите ваш login и пароль через пробел (например, login password):')
    bot_tg.register_next_step_handler(message, process_login_password)


def validate(message):
    bot_tg.send_message(message.from_user.id, 'Пароль должен содержать только '
                                              'латинские символы в верхнем и нижнем регистре, '
                                              'цифры и как минимум один специальный символ'
                                              'и иметь длину не менее 8 символов. '
                                              'Введите ваш login и пароль через пробел')
    bot_tg.register_next_step_handler(message, process_login_password)


def check_username_set(message):
    user = message.from_user
    if user.username is None:
        bot_tg.send_message(user.id, 'Пожалуйста, установите username в настройках Telegram.')
        bot_tg.register_next_step_handler(message, check_username_set, bot_tg)
    else:
        start_auth(message)


def process_login_password(message):
    user = message.from_user
    session = Session()
    login_password = message.text.split()
    if len(login_password) != 2:
        bot_tg.send_message(user.id, 'Неправильный формат ввода. Введите login и пароль через пробел.')
        bot_tg.register_next_step_handler(message, process_login_password)
    else:
        login, password = login_password
        db_user = session.query(User).filter_by(username=user.username).first()
        if db_user:
            if db_user.login != login or db_user.password != hash_password(password):
                bot_tg.send_message(user.id, 'Неверный логин или пароль. Попробуйте снова.')
                bot_tg.register_next_step_handler(message, authenticate)
            else:
                bot_tg.send_message(user.id, 'Вы успешно авторизованы!')
                create_buttons(message)
        else:
            db_user = session.query(User).filter_by(login=login, password=hash_password(password)).first()
            if db_user:
                db_user.username = user.username
                session.commit()
                bot_tg.send_message(user.id, 'Данные тг аккаунта добавлены для входа. Вы успешно авторизованы!')
            else:
                if not valid(password):
                    bot_tg.send_message(user.id, 'Не валидный пароль.')
                    validate(message)
                else:
                    new_user = User(username=user.username, login=login, password=hash_password(password))
                    session.add(new_user)
                    session.commit()
                    bot_tg.send_message(user.id,
                                        'Пользователь успешно добавлен в базу данных.\nВы успешно авторизованы!')
                    create_buttons(message)


def valid(password):
    pattern = re.compile(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=_!])[A-Za-z0-9@#$%^&+=_!]{8,}')
    return bool(pattern.fullmatch(password))


def hash_password(password):
    password_bytes = password.encode('utf-8')
    sha256 = hashlib.sha256()

    sha256.update(password_bytes)
    hashed_password = sha256.hexdigest()

    return hashed_password
