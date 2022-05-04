import logging
import os
import socket
import sys
from functools import wraps

from PyQt5.QtWidgets import QMessageBox
from .variables import AUTH, REG

sys.path.append(os.path.join(os.getcwd(), '..'))
from log import server_log_config

if sys.argv[0].find('client.py') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


def login_required(func):
    """Декоратор, проверяющий авторизацию клиента на сервере.
    Пропускает PRESENCE, AUTH, REG сообщения. Для остальных сообщений проверят наличие
    сокета клиента в dict подключенных к серверу пользователей.
    """

    def wrap(*args, **kwargs):
        from .variables import ACTION, PRESENCE
        sys.path.append(os.path.join(os.getcwd(), '..'))
        from server import Server
        if isinstance(args[0], Server):
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] in (PRESENCE, AUTH, REG):
                        return func(*args, **kwargs)

                if isinstance(arg, socket.socket):
                    for client in args[0].clients_dict:
                        if args[0].clients_dict[client] == arg:
                            return func(*args, **kwargs)
        return

    return wrap


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
