import time
from datetime import datetime

import schedule

from bot_data import bot_tg
from database import Session, User


def process_reminder_time(message):
    user = message.from_user
    session = Session()
    try:
        reminder_time = datetime.strptime(message.text, '%H:%M')
        db_user = session.query(User).filter_by(username=user.username).first()
        if db_user:
            db_user.reminder_time = reminder_time
            session.commit()
            bot_tg.send_message(user.id, f'Время напоминания установлено на {message.text}')
            schedule.clear(f'{user.id}_reminder')
            schedule.every().day.at(message.text).do(send_reminder, user_id=user.id).tag(f'{user.id}_reminder')
        else:
            bot_tg.send_message(user.id, 'Чтобы установить напоминание, сначала зарегистрируйтесь с помощью /start.')
    except ValueError:
        bot_tg.send_message(user.id, 'Неправильный формат времени. Пожалуйста, введите время в формате HH:MM.')


def send_reminder(user_id):
    bot_tg.send_message(user_id, 'Пора проверить бота!')


def start_check_reminders():
    while True:
        schedule.run_pending()
        time.sleep(30)
