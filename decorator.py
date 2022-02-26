import logging
import sys
import log.server_log_config
import log.client_log_config
from functools import wraps

if sys.argv[0].find('client.py') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


def logs(func):
    """Декоратор для вывода"""

    @wraps(func)
    def wrap(*args, **kwargs):
        res = func(*args, **kwargs)
        fmt = logging.Formatter("%(asctime)s - %(message)s", "%d.%m.%Y %H:%M:%S")
        logger.handlers[0].setFormatter(fmt)
        logger.handlers[1].setFormatter(fmt)
        logger.debug(f'Функция {func.__name__} вызвана функцией {sys._getframe().f_back.f_code.co_name}, '
                     f'из файла {sys._getframe().f_back.f_code.co_filename.split("/")[-1]} '
                     f'с параметрами *args = {args}, **kwargs {kwargs}')

        # logger.info(f'Функция {func.__name__} вызвана из функции {sys._getframe().f_back.f_code.co_name}')
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(module)s - %(message)s", "%d.%m.%Y %H:%M:%S")
        logger.handlers[0].setFormatter(fmt)
        logger.handlers[1].setFormatter(fmt)
        return res

    return wrap


@logs
def foo(a):
    print('Выполнение функции c gfhfvtnhjv - ', a)
