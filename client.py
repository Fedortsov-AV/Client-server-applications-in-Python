import sys
from socket import socket, AF_INET, SOCK_STREAM

from common.utils import send_message, get_message
from common.variables import DEFAULT_PORT, DEFAULT_ADR, VALID_ADR, VALID_PORT, ALERT, ACTION, USER, RESPONCE


def presence_msg():
    msg = {
        ACTION: 'presence',
        USER: 'guest'
    }
    return msg


def parcing_msg(input_date: dict):
    if isinstance(input_date, dict):
        if input_date[RESPONCE] and input_date[ALERT]:
            return print(f'{input_date[RESPONCE]} : {input_date[ALERT]}')
    return print()


if VALID_ADR.findall(sys.argv[1]):
    ADDRES = VALID_ADR.findall(sys.argv[1])[0]
else:
    ADDRES = DEFAULT_ADR
    print('Установлен ip-адрес \'%s\', в строке параметров отсутствует задание ip-адреса соответствующее шаблону' % (
        DEFAULT_ADR))

if VALID_PORT.findall(sys.argv[2]):
    PORT = int(VALID_PORT.findall(sys.argv[2])[0])
else:
    PORT = int(DEFAULT_PORT)
    print('Установлен ip-адрес \'%s\', в строке параметров отсутствует задание ip-адреса соответствующее шаблону' % (
        DEFAULT_ADR))

# print('%s:%d' % (ADDRES, PORT))
SRVSOCK = socket(AF_INET, SOCK_STREAM)
SRVSOCK.connect((ADDRES, PORT))
PRESENCE_MSG = presence_msg()
PRESENCE_MSG = {ACTION: 'presence'}
send_message(PRESENCE_MSG, SRVSOCK)
data = get_message(SRVSOCK)
parcing_msg(data)
