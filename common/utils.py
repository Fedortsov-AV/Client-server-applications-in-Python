import json
import socket

from common.variables import MAX_LEN_MSG, ENCODE


def send_message(msg: dict, sock: socket.socket):
    if isinstance(msg, dict) and isinstance(sock, socket.socket):
        json_msg = json.dumps(msg).encode(ENCODE)
        sock.send(json_msg)
    else:
        return print('Неверный тип данных передан в аргументы функции send_message(msg: dict, sock: socket.socket)')

def get_message(sock):
    byte_json_msg = sock.recv(MAX_LEN_MSG)
    json_msg = byte_json_msg.decode(ENCODE)
    data = json.loads(json_msg)
    return data
