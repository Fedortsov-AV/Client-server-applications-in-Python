import json
import os
import socket
import sys

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import MAX_LEN_MSG, ENCODE, ANS_104, ANS_105

from decorator import logs


@logs
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
        if sys.exc_info()[0] in (TypeError, ValueError):
            # print('send: ', sys.exc_info()[0])
            return send_message(ANS_105, sock)

        if sys.exc_info()[0] in (ConnectionResetError, OSError):
            # print('send: ', sys.exc_info()[0])
            return send_message(ANS_104, sock)


@logs
def get_message(sock: socket.socket):
    # print(f'get message sock - {sock}')
    data = {}
    try:
        if isinstance(sock, socket.socket):
            byte_json_msg = sock.recv(MAX_LEN_MSG)
            json_msg = byte_json_msg.decode(ENCODE)
            data = json.loads(json_msg)
            if isinstance(data, dict):
                return data
            return print('Получена неверная структура JSON')
        return print('Неверный тип данных передан в аргументы функции get_message(sock: socket.socket)')
    finally:
        if sys.exc_info()[0] in (TypeError, ValueError):
            # print('get: ', sys.exc_info()[0])
            return print(sys.exc_info()[0])

        if sys.exc_info()[0] in (ConnectionResetError, OSError):
            # print('get: ', sys.exc_info()[0])
            return print(sys.exc_info()[0])
