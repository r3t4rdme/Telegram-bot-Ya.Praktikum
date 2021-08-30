import logging
import os
import time
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

current_timestamp = int(time.time())

bot = telegram.Bot(token=TELEGRAM_TOKEN)

url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

logging.basicConfig(level=logging.DEBUG,
                    filename='program.log',
                    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s')

# а тут настраиваем логгер для текущего файла .py
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'my_logger.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)


def parse_homework_status(homework):
    print(homework)
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    homework_statuses = {
        'approved': 'Ревьюеру всё понравилось, работа зачтена!',
        'rejected': 'К сожалению, в работе нашлись ошибки.',
        'reviewing': 'Проект на стадии ревью'
    }
    if homework_name is None:
        message: str = 'Работа не найдена'
        logger.error(message)
        send_message(message)
    if homework_status in homework_statuses:
        verdict = homework_statuses[homework_status]
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    message: str = 'Неизвестный статус'
    logger.error(message)
    send_message(message)


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
        return homework_statuses.json()
    except requests.exceptions.RequestException as e:
        raise e('Ошибка при запросе сервера Практикума')


def send_message(message):
    logger.info('Бот отправил сообщение.')
    return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # Начальное значение timestamp
    seconds_in_month = 60 * 60 * 24 * 30 * 150
    time_brackets = current_timestamp - seconds_in_month
    while True:
        logger.debug('Бот начал работу.')
        try:
            send_message(
                parse_homework_status(
                    get_homeworks(time_brackets)
                ))
            time.sleep(5 * 5)  # Опрашивать раз в пять минут
        except Exception as e:
            error_message = e('Бот упал с ошибкой')
            logger.error(error_message)
            send_message(chat_id=TELEGRAM_CHAT_ID, text=error_message)
            time.sleep(5)


if __name__ == '__main__':
    main()
