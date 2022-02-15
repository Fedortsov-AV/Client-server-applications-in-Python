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
                    return f'{timeserv} - {input_date[RESPONCE]} : {input_date[ALERT]}'
                raise ValueError
            raise KeyError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (KeyError, TypeError, ValueError):
            return 'Неправильный ответ/JSON-объект'


def parce_addres_in_cmd(arg: list):
    if VALID_ADR.findall(arg[1]):
        if VALID_ADR.findall(arg[1])[0]:
            ADDRES = VALID_ADR.findall(arg[1])[0]
            return ADDRES
        else:
            ADDRES = DEFAULT_ADR
            return ADDRES
    else:
        ADDRES = DEFAULT_ADR
        print(
            'Установлен ip-адрес \'%s\', в строке параметров отсутствует задание ip-адреса соответствующее шаблону' % (
                DEFAULT_ADR))
        return ADDRES


def parce_port_in_cmd(arg: list):
    if VALID_PORT.findall(arg[2]):
        if VALID_PORT.findall(arg[2])[0]:
            PORT = int(VALID_PORT.findall(arg[2])[0])
            return PORT

    else:
        PORT = int(DEFAULT_PORT)
        print(
            'Установлен ip-адрес \'%s\', в строке параметров отсутствует задание ip-адреса соответствующее шаблону' % (
                DEFAULT_ADR))
        return PORT


def main():
    ADDRES = parce_addres_in_cmd(sys.argv)
    PORT = parce_port_in_cmd(sys.argv)

    # print('%s:%d' % (ADDRES, PORT))
    SRVSOCK = socket(AF_INET, SOCK_STREAM)
    SRVSOCK.connect((ADDRES, PORT))
    PRESENCE_MSG = presence_msg()
    send_message(PRESENCE_MSG, SRVSOCK)
    data = get_message(SRVSOCK)
    print(parcing_msg(data))


if __name__ == '__main__':
    main()
