import logging
import os
import sys
from functools import wraps

from PyQt5.QtWidgets import QMessageBox
sys.path.append(os.path.join(os.getcwd(), '..'))

from log import client_log_config


logger = logging.getLogger('client')


def logs(func):
    """Декоратор для вывода в лог сообщения
    с указанием функции вызвавшей декарируемую функцию"""

    @wraps(func)
    def wrap(*args, **kwargs):
        res = func(*args, **kwargs)
        fmt = logging.Formatter("%(asctime)s - %(message)s", "%d.%m.%Y %H:%M:%S")
        logger.handlers[0].setFormatter(fmt)
        logger.handlers[1].setFormatter(fmt)
        logger.debug(f'Функция {func.__name__} вызвана функцией {sys._getframe().f_back.f_code.co_name}, '
                     f'из файла {sys._getframe().f_back.f_code.co_filename.split("/")[-1]} '
                     f'с параметрами *args = {args}, **kwargs {kwargs}')
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(module)s - %(message)s", "%d.%m.%Y %H:%M:%S")
        logger.handlers[0].setFormatter(fmt)
        logger.handlers[1].setFormatter(fmt)
        return res

    return wrap


def verify_edit(func):
    """Декоратор находит все поля типа Edit и проверяет данные в них.
    :returns: В случае успеха возвращает результат декорируемой функции.
    Если поля пустые или содержат недопустимые данные возвращает QMessageBox"""

    def wrap(self):
        for key in self.__dict__:
            if 'QLineEdit' in str(self.__dict__[key]):
                if self.__dict__[key].text() == '':
                    return QMessageBox.critical(self,
                                                "Предупреждение",
                                                "Имя и пароль не могут быть пустыми!",
                                                QMessageBox.Ok)
                if len(self.__dict__[key].text()) < 3:
                    return QMessageBox.critical(self,
                                                "Предупреждение",
                                                "Длина имени и пароля должны быть не менее 3х символов!",
                                                QMessageBox.Ok)
                for _ in (';', ':', '==', '"'):
                    if _ in self.__dict__[key].text():
                        return QMessageBox.critical(self,
                                                    "Предупреждение",
                                                    f"Имя или пароль содержат недопустимый символ \" {_} \"!",
                                                    QMessageBox.Ok)
        res = func(self)
        return res

    return wrap


if __name__ == '__main__':
    @logs
    def foo(a):
        print('Выполнение функции c gfhfvtnhjv - ', a)