import json
import socket
import sys

from common.variables import MAX_LEN_MSG, ENCODE


def send_message(msg: dict, sock: socket.socket):
    try:
        if isinstance(msg, dict) and isinstance(sock, socket.socket):
            json_msg = json.dumps(msg).encode(ENCODE)
            if isinstance(json_msg, bytes):
                sock.send(json_msg)
                return 'Отправка успешна'
            raise TypeError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (TypeError, ValueError, OSError):
            print('send: ', sys.exc_info()[0])
            return 'Ошибка отправки'


def get_message(sock: socket.socket):
    try:
        if isinstance(sock, socket.socket):
            byte_json_msg = sock.recv(MAX_LEN_MSG)
            json_msg = byte_json_msg.decode(ENCODE)
            data = json.loads(json_msg)
            if isinstance(data, dict):
                # print(type(data))
                return data
            return print('Получена неверная структура JSON')
        return print('Неверный тип данных передан в аргументы функции get_message(sock: socket.socket)')
    finally:
        if sys.exc_info()[0] in (TypeError, ValueError, OSError):
            print('get: ', sys.exc_info()[0])
            return 'Ошибка получения'
