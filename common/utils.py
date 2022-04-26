"""Модуль хранит общие функции для сервера и клиента"""

import json
import os
import socket
import sys

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import MAX_LEN_MSG, ENCODE, ANS_104, ANS_105, ANS_400

from decorator import logs


@logs
def send_message(msg: dict, sock: socket.socket) -> bool:
    """
    Функция для отправки сообщения, создает JSON из dict, кодирует его в байты и отправляет в адрес сокета

    :param msg: dict для создания JSON
    :param sock: сокет, в который необходимо отправить байты
    :return: Возвращает True, если отправка успешна, либо False если произошла ошибка
    """
    try:
        if isinstance(msg, dict) and isinstance(sock, socket.socket):
            json_msg = json.dumps(msg).encode(ENCODE)
            if isinstance(json_msg, bytes):
                if sock:
                    sock.send(json_msg)
                return True
            raise TypeError
        raise TypeError
    except Exception as e:
        return False
    finally:
        if sys.exc_info()[0] in (TypeError, ValueError) and sock:
            return False

        if sys.exc_info()[0] in (ConnectionResetError, OSError) and sock:
            return False


@logs
def get_message(sock: socket.socket) -> dict:
    """
    Функция для получения данных из сокета и преобразования полученных байтов в dict
    :param sock: сокет из которого получаем данные
    :return: При удачном получении данных возвращает dict c полученным данными.
    При исключениях TypeError или ValueError возвращает словарь:
    ANS_400 = {
    ACTION: ALERT,
    RESPONSE: 400,
    ALERT: 'Неправильный запрос/JSON-объект',
    TIME: time.time()
    }
    При исключениях ConnectionResetError, OSErrorr возвращает словарь:
    ANS_104 = {
    ACTION: ALERT,
    RESPONSE: 104,
    ALERT: 'ConnectionResetError',
    TIME: time.time()
    }
    """

    try:
        if isinstance(sock, socket.socket):
            byte_json_msg = sock.recv(MAX_LEN_MSG)
            json_msg = byte_json_msg.decode(ENCODE)
            data = json.loads(json_msg)
            if isinstance(data, dict):
                return data
            return ANS_400
        return ANS_400
    finally:
        if sys.exc_info()[0] in (TypeError, ValueError):
            return ANS_400
        if sys.exc_info()[0] in (ConnectionResetError, OSError):
            return ANS_104
