import sys
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM

from common.utils import send_message, get_message
from common.variables import PASSWORD, TIME, AUTHUSER, DEFAULT_PORT, DEFAULT_ADR, VALID_ADR, VALID_PORT, ALERT, ACTION, \
    USER, RESPONCE


def presence_msg():
    msg = {
        ACTION: 'presence',
        TIME: time.time(),
        USER: {
            AUTHUSER: 'guest',
            PASSWORD: ''
        }
    }
    return msg


def parcing_msg(input_date: dict):
    try:
        if isinstance(input_date, dict):
            if input_date[RESPONCE] and input_date[ALERT] and input_date[TIME]:
                if isinstance(input_date[TIME], float):
                    timeserv = time.strftime('%d.%m.%Y %H:%M', time.localtime(input_date[TIME]))
                    return print(f'{timeserv} - {input_date[RESPONCE]} : {input_date[ALERT]}')
                raise ValueError
            raise KeyError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (KeyError, TypeError, ValueError):
            return print('Неправильный ответ/JSON-объект')


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
print(PRESENCE_MSG)
send_message(PRESENCE_MSG, SRVSOCK)
data = get_message(SRVSOCK)
parcing_msg(data)
