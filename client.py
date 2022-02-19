import sys
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
from log.client_log_config import client_log as log
from common.utils import send_message, get_message
from common.variables import PASSWORD, TIME, ACCOUNT_NAME, DEFAULT_PORT, DEFAULT_ADR, VALID_ADR, VALID_PORT, ALERT, \
    ACTION, USER, RESPONSE


def presence_msg():
    msg = {
        ACTION: 'presence',
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: 'guest',
            PASSWORD: ''
        }
    }
    log.debug(f'сформировано сообщение {msg}')
    return msg


def parsing_msg(input_date: dict):
    log.debug(f'Получен аргумент {input_date}')
    try:
        if isinstance(input_date, dict):
            if input_date[RESPONSE] and input_date[ALERT] and input_date[TIME]:
                if isinstance(input_date[TIME], float):
                    timeserv = time.strftime('%d.%m.%Y %H:%M', time.localtime(input_date[TIME]))
                    return f'{timeserv} - {input_date[RESPONSE]} : {input_date[ALERT]}'
                raise ValueError
            raise KeyError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (KeyError, TypeError, ValueError):
            log.critical(f'Произошла ошибка {sys.exc_info()[0]}')
            return 'Неправильный ответ/JSON-объект'


def parse_addres_in_cmd(arg: list):
    log.debug(f'Получен аргумент {arg}')
    try:
        if isinstance(arg, list):
            if VALID_ADR.findall(arg[1]):
                if VALID_ADR.findall(arg[1])[0]:
                    addres = VALID_ADR.findall(arg[1])[0]
                    log.info(f'Установлен ip-адрес {addres}')
                    return addres
                raise ValueError
            raise IndexError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (IndexError, TypeError, ValueError):
            addres = DEFAULT_ADR
            log.critical(f'Произошла ошибка {sys.exc_info()[0]}, установлен ip-адрес {addres}')
            return addres


def parse_port_in_cmd(arg: list):
    log.debug(f'Получен аргумент {arg}')
    try:
        if isinstance(arg, list):
            if VALID_PORT.findall(arg[2]):
                if VALID_PORT.findall(arg[2])[0]:
                    port = int(VALID_PORT.findall(arg[2])[0])
                    if 1024 < port < 65535:
                        log.info(f'Установлен порт {port}')
                        return port
                    raise ValueError
                raise IndexError
            raise IndexError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (IndexError, TypeError, ValueError):
            port = int(DEFAULT_PORT)
            log.critical(f'Произошла ошибка {sys.exc_info()[0]}, установлен порт {port}')
            return port


def main():
    addres = parse_addres_in_cmd(sys.argv)
    port = parse_port_in_cmd(sys.argv)
    log.info(f'Сокет будет привязан к  {(addres, port)}')
    clientsock = socket(AF_INET, SOCK_STREAM)
    clientsock.connect((addres, port))
    presence_message = presence_msg()
    log.info('Отправляю сообщение на сервер')
    send_message(presence_message, clientsock)
    log.info('Получаю сообщение с сервера')
    data = get_message(clientsock)
    log.info('Разбираю ответ сервера')
    print(parsing_msg(data))



if __name__ == '__main__':
    main()
