import json
import socket

from common.variables import MAX_LEN_MSG, ENCODE


def send_message(msg: dict, sock: socket.socket):
    if isinstance(msg, dict) and isinstance(sock, socket.socket):
        json_msg = json.dumps(msg).encode(ENCODE)
        sock.send(json_msg)
        return
    return print('Неверный тип данных передан в аргументы функции send_message(msg: dict, sock: socket.socket)')


def get_message(sock: socket.socket):
    if isinstance(sock, socket.socket):
        byte_json_msg = sock.recv(MAX_LEN_MSG)
        json_msg = byte_json_msg.decode(ENCODE)
        data = json.loads(json_msg)
        return data
    return print('Неверный тип данных передан в аргументы функции sget_message(sock: socket.socket)')
