import logging
import logging.handlers
from django.conf import settings

import os

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename='logs/app.log', level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Это тестовое сообщение для логирования в файл")

# Создаем основной логгер Django
logger = logging.getLogger('django')

# Устанавливаем уровень логирования основного логгера Django
logger.setLevel(logging.DEBUG)

# Создаем обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Создаем форматтер для вывода в консоль
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Создаем фильтр для вывода в консоль только при DEBUG = True
class DebugFilter(logging.Filter):
    def filter(self, record):
        return not settings.DEBUG

debug_filter = DebugFilter()
console_handler.addFilter(debug_filter)

# Добавляем обработчик вывода в консоль к основному логгеру Django
logger.addHandler(console_handler)

# Создаем обработчик и форматтер для файла general.log
general_handler = logging.handlers.RotatingFileHandler('logs/general.log', maxBytes=1024*1024, backupCount=5)
general_handler.setLevel(logging.INFO)
general_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
general_handler.setFormatter(general_formatter)

# Добавляем обработчик файла к основному логгеру Django
logger.addHandler(general_handler)

# Создаем обработчик и форматтер для файла errors.log
errors_handler = logging.handlers.RotatingFileHandler('logs/errors.log', maxBytes=1024*1024, backupCount=5)
errors_handler.setLevel(logging.ERROR)
errors_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s - %(pathname)s\n%(exc_info)s')
errors_handler.setFormatter(errors_formatter)

# Создаем фильтр для файла errors.log, чтобы записывались только ошибки
class ErrorsFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR

errors_filter = ErrorsFilter()
errors_handler.addFilter(errors_filter)

# Добавляем обработчик файла ошибок к основному логгеру Django
logger.addHandler(errors_handler)

# Создаем отдельный логгер для безопасности
security_logger = logging.getLogger('django.security')
security_logger.setLevel(logging.DEBUG)

# Создаем обработчик и форматтер для файла security.log
security_handler = logging.handlers.RotatingFileHandler('logs/security.log', maxBytes=1024*1024, backupCount=5)
security_handler.setLevel(logging.DEBUG)
security_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
security_handler.setFormatter(security_formatter)

# Добавляем обработчик файла безопасности к логгеру безопасности
security_logger.addHandler(security_handler)

# Создаем обработчик для отправки почты
mail_handler = logging.handlers.SMTPHandler(
    mailhost='smtp.yandex.ru',
    fromaddr='@yandex.ru',
    toaddrs=['@yandex.ru'],
    subject='Ошибка',
    credentials=('@yandex.ru', ''),
    secure=(),
    timeout=5
)

# Добавляем обработчик отправки почты к основному логгеру Django
logger.addHandler(mail_handler)
mail_handler.setLevel(logging.ERROR)
mail_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s - %(pathname)s\n%(exc_info)s')
mail_handler.setFormatter(mail_formatter)

# Добавляем обработчик отправки почты к основному логгеру Django
logger.addHandler(mail_handler)

try:
    # Генерируем исключение для тестирования записи ошибки в файл 'general.log'
    raise ValueError('Тестовая ошибка')
except Exception as e:
    # Записываем ошибку в файл 'general.log'
    logger.error("Произошла ошибка: %s", str(e))
