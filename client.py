import logging
import sys
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread

import log.client_log_config
from common.utils import send_message, get_message
from common.variables import PASSWORD, TIME, ACCOUNT_NAME, DEFAULT_PORT, DEFAULT_ADR, VALID_ADR, VALID_PORT, ALERT, \
    ACTION, USER, RESPONSE, MESSAGE_TEXT, FROM
from decorator import logs


logger = logging.getLogger('client')


@logs
def presence_msg() -> dict:
    msg = {}
    msg = {
        ACTION: 'presence',
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: user_name,
            PASSWORD: ''
        }
    }
    logger.debug(f'сформировано сообщение {msg}')
    return msg

@logs
def generation_msg(message: str, name: str) -> dict:
    msg = {}
    if message == 'exit':
        msg = {
            ACTION: 'EXIT',
            TIME: time.time(),
            ACCOUNT_NAME: user_name,
        }
        logger.info('Закрываю скрипт')
    else:
        msg = {
            ACTION: 'MESSAGE',
            TIME: time.time(),
            ACCOUNT_NAME: user_name,
            MESSAGE_TEXT: message,
            FROM: name,
        }
    logger.debug(f'сформировано сообщение {msg}')
    return msg

@logs
def parsing_msg(input_date: dict):
    logger.debug(f'Получен аргумент {input_date}')
    try:
        if isinstance(input_date, dict):
            if input_date[RESPONSE] in (200, 400) and input_date[ALERT] and input_date[TIME]:
                if isinstance(input_date[TIME], float):
                    timeserv = time.strftime('%d.%m.%Y %H:%M', time.localtime(input_date[TIME]))
                    logger.info(f'{timeserv} - {input_date[RESPONSE]} : {input_date[ALERT]}')
                    return
            elif input_date[RESPONSE] in (104, 105) and input_date[ALERT] and input_date[TIME]:
                    if isinstance(input_date[TIME], float):
                        timeserv = time.strftime('%d.%m.%Y %H:%M', time.localtime(input_date[TIME]))
                        logger.info(f'{timeserv} - {input_date[RESPONSE]} : {input_date[ALERT]}')
                        sys.exit(0)

            elif input_date[RESPONSE] == 'message' and input_date[FROM] and input_date[MESSAGE_TEXT] and input_date[ACCOUNT_NAME]:
                return f"{input_date[ACCOUNT_NAME]} написал: {input_date[MESSAGE_TEXT]}"
            raise ValueError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (KeyError, TypeError, ValueError):
            logger.critical(f'Произошла ошибка {sys.exc_info()[0]}')
            return 'Неправильный ответ/JSON-объект'


@logs
def parse_addres_in_cmd(arg: list):
    # logger.debug(f'Получен аргумент {arg}')
    try:
        if isinstance(arg, list):
            if VALID_ADR.findall(arg[1]):
                if VALID_ADR.findall(arg[1])[0]:
                    addres = VALID_ADR.findall(arg[1])[0]
                    logger.info(f'Установлен ip-адрес {addres}')
                    return addres
                raise ValueError
            raise IndexError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (IndexError, TypeError, ValueError):
            addres = DEFAULT_ADR
            logger.critical(f'Произошла ошибка {sys.exc_info()[0]}, установлен ip-адрес {addres}')
            return addres


@logs
def parse_port_in_cmd(arg: list):
    logger.debug(f'Получен аргумент {arg}')
    try:
        if isinstance(arg, list):
            if VALID_PORT.findall(arg[2]):
                if VALID_PORT.findall(arg[2])[0]:
                    port = int(VALID_PORT.findall(arg[2])[0])
                    if 1024 < port < 65535:
                        logger.info(f'Установлен порт {port}')
                        return port
                    raise ValueError
                raise IndexError
            raise IndexError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (IndexError, TypeError, ValueError):
            port = int(DEFAULT_PORT)
            logger.critical(f'Произошла ошибка {sys.exc_info()[0]}, установлен порт {port}')
            return port

def get_server_msg(clientsock: socket):
    logger.debug('Жду данные от сервера')
    while True:
        data = get_message(clientsock)
        logger.debug('Разбираю ответ сервера')
        print(parsing_msg(data))

def send_msg(clientsock):
    while True:
        name = input('Кому отправить сообщение?\n ')
        logger.debug('Формирую сообщение пользователя')
        str = input('Введите сообщение для отправки (для выхода введите \'exit\'): \n')
        message = generation_msg(str, name)
        logger.debug('Отправляю сообщение на сервер')
        send_message(message, clientsock)
        if message[ACTION] == 'EXIT':
            time.sleep(0.7)
            break



def main():
    addres = parse_addres_in_cmd(sys.argv)
    port = parse_port_in_cmd(sys.argv)

    logger.info(f'Сокет будет привязан к  {(addres, port)}')
    with socket(AF_INET, SOCK_STREAM) as clientsock:
        clientsock.connect((addres, port))
        clientsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        pres = presence_msg()
        send_message(pres, clientsock)
        parsing_msg(get_message(clientsock))

        get = Thread(target=get_server_msg, args=(clientsock,), daemon=True, name='get')
        send = Thread(target=send_msg, args=(clientsock,), daemon=True, name='send')
        get.start()
        send.start()

        while True:
            time.sleep(1)
            if get.is_alive() and send.is_alive():

                continue
            break



if __name__ == '__main__':
    user_name = input('Введите ваше имя: ')
    main()
