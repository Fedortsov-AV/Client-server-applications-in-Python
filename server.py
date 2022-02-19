import sys
from socket import socket, AF_INET, SOCK_STREAM

from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, VALID_ADR, VALID_PORT, ANS_200, ANS_400, ACTION, USER, TIME, ACCOUNT_NAME
from log.server_log_config import server_log as srv_log


def parsing_msg(input_date: dict):
    try:
        if isinstance(input_date, dict):
            if input_date[ACTION] and input_date[USER][ACCOUNT_NAME] and input_date[TIME]:
                if input_date[ACTION] == 'presence' and input_date[USER][ACCOUNT_NAME] == 'guest':
                    srv_log.debug(f'Сообщение клиента соответствует требованиям, отвечаю {ANS_200}')
                    return ANS_200
                raise ValueError
            raise KeyError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (KeyError, TypeError, ValueError):
            srv_log.critical(f'Произошла ошибка: {sys.exc_info()[0]}')
            return ANS_400


def parse_addres_in_argv(arg: list):
    srv_log.debug(f'Получен аргумент: {arg}')
    try:
        if isinstance(arg, list):
            if '-a' in arg:
                if VALID_ADR.findall(arg[sys.argv.index('-a') + 1]):
                    if VALID_ADR.findall(arg[arg.index('-a') + 1])[0]:
                        ADDRES = VALID_ADR.findall(arg[arg.index('-a') + 1])[0]
                        srv_log.debug(f'В командной строке задан ip-адрес: {ADDRES}')
                        return ADDRES
                    raise ValueError
                raise IndexError
            raise IndexError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (IndexError, TypeError, ValueError):
            ADDRES = ''
            srv_log.warning(f'Установлен адрес: {ADDRES}')
            return ADDRES


def parse_port_in_argv(arg: list):
    srv_log.debug(f'Получен аргумент: {arg}')
    try:
        if isinstance(arg, list):
            if '-p' in arg:
                if VALID_PORT.findall(arg[sys.argv.index('-p') + 1]):
                    if VALID_PORT.findall(arg[arg.index('-p') + 1])[0]:
                        PORT = int(VALID_PORT.findall(arg[arg.index('-p') + 1])[0])
                        if PORT > 1024 or PORT < 65535:
                            PORT = int(DEFAULT_PORT)
                            srv_log.debug(f'В командной строке задан порт: {PORT}')
                            return PORT
                        raise ValueError
                    raise ValueError
                raise IndexError
            raise IndexError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (IndexError, TypeError, ValueError):
            PORT = int(DEFAULT_PORT)
            srv_log.warning(f'Установлен порт: {PORT}')
            return PORT


def main():
    ADDRES = parse_addres_in_argv(sys.argv)
    PORT = parse_port_in_argv(sys.argv)
    srv_log.info(f'Сокет будет привязан к  {(ADDRES, PORT)}')
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((ADDRES, PORT))
    s.listen(5)
    while True:
        client, addr = s.accept()
        srv_log.info(f"Запрос на соединение от {addr}")
        try:
            data = get_message(client)
            srv_log.info(f'Сообщение: {data} было отправлено клиентом: {addr}')
            msg = parsing_msg(data)
            send_message(msg, client)
            srv_log.info(f'Закрываю соединение с {addr}')
            client.close()
        except ConnectionResetError:
            srv_log.error('Произошла ошибка ConnectionResetError, закрываю соединение с клиентом')
            client.close()


if __name__ == '__main__':
    main()
