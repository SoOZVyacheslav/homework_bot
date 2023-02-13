import logging
import os
import sys
import time
from http import HTTPStatus

import exceptions
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_ID')
TELEGRAM_TOKEN = os.getenv('BOT_ID')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s - %(name)s',
    level=logging.INFO,
    filename='bot.log',
    filemode='w',
    encoding='utf--8',
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def check_tokens():
    """Проверяем токены."""
    return all({PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID})


def send_message(bot, message):
    """Отправляет сообщение в телеграм."""
    try:
        logger.debug(f'Сообщение отправлено: {message}')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.TelegramError as error:
        logger.error(f'Cообщение не отправленно: {error}')


def get_api_answer(timestamp):
    """Получить ответ от сервера практикума по API."""
    current_timestamp = timestamp
    params_request = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': current_timestamp}
    }
    try:
        response = requests.get(**params_request)
        message = (
            'Начал выполняться запрос: {url}, {headers}, {params}.'
        ).format(**params_request)
        logging.info(message)
    except requests.exceptions.RequestException:
        raise exceptions.ApiException(
            'API недоступна'
            f'{ENDPOINT}'
        )
    finally:
        if response.status_code != HTTPStatus.OK:
            raise exceptions.ApiException(
                f'{response.status_code} Проблема с доступом к странице'
            )
    return response.json()


def check_response(response):
    """Проверяем ответ API."""
    if type(response) != dict:
        raise TypeError('Запрос не в виде словаря')
    homeworks = response.get('homeworks')
    if homeworks is None:
        raise exceptions.CheckResponseException(
            'Нет ключа homeworks в ответе от API')
    if type(homeworks) != list:
        logger.error('Запрос не в виде списка')
        raise TypeError
    return homeworks


def parse_status(homework):
    """Проверяем статус."""
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise KeyError('Нет данных о работе')
    homework_statuses = homework.get('status')
    if homework_statuses is None:
        raise KeyError('Нет данных о статусе')
    verdict = HOMEWORK_VERDICTS.get(homework_statuses)
    if verdict is None:
        raise exceptions.StatusException('Недокументированный статус')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствуют токены. Запрос остановлен')
        sys.exit(0)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                for homework in homeworks:
                    message = parse_status(homework)
                    send_message(bot, message)
                logger.info('Повторный запрос через 10 минут')
            else:
                logger.info('Отсутствует новая информация')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logger.error(message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
