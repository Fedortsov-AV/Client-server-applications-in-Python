import logging
import sys
from select import select
from socket import socket, AF_INET, SOCK_STREAM

from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, VALID_ADR, VALID_PORT, ANS_200, ANS_400, ACTION, USER, TIME, ACCOUNT_NAME, \
    MESSAGE_TEXT, FROM, RESPONSE
from decorator import logs
import log.server_log_config


srv_log = logging.getLogger('server')


@logs
def parsing_msg(input_date: dict, sock: socket, message_list: list):
    # srv_log.debug(f'Получен аргумент: {input_date}')
    try:
        if isinstance(input_date, dict):
            if input_date[ACTION] == 'presence' and input_date[USER][ACCOUNT_NAME] == 'guest' and input_date[TIME]:

                srv_log.debug(f'Сообщение клиента соответствует требованиям, отвечаю {ANS_200}')
                return send_message(ANS_200, sock)
            elif input_date[ACTION] == 'MESSAGE' and input_date[ACCOUNT_NAME] and input_date[MESSAGE_TEXT]:
                message_list.append([input_date[ACCOUNT_NAME], input_date[MESSAGE_TEXT]])
                return message_list
            raise KeyError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (KeyError, TypeError, ValueError):
            srv_log.critical(f'Произошла ошибка: {sys.exc_info()[0]}')
            return send_message(ANS_400, sock)


@logs
def parse_addres_in_argv(arg: list):
    # srv_log.debug(f'Получен аргумент: {arg}')
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


@logs
def parse_port_in_argv(arg: list):
    # srv_log.debug(f'Получен аргумент: {arg}')
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




def serv_acept(s: socket, clients: list):
    try:
        client, addr = s.accept()
    except OSError as e:
        # srv_log.debug(f"Ошибка {e}")
        return clients
    else:
        srv_log.info(f"Запрос на соединение от {addr}")
        clients.append(client)
        return clients








def main():
    ADDRES = parse_addres_in_argv(sys.argv)
    PORT = parse_port_in_argv(sys.argv)
    srv_log.info(f'Сокет будет привязан к  {(ADDRES, PORT)}')
    with socket(AF_INET, SOCK_STREAM) as s:
        s.settimeout(0.5)
        s.bind((ADDRES, PORT))
        s.listen(5)
        clients = []
        message_list = []
        while True:
            # finally:
            wait = 0
            write = []
            read = []
            try:
                clients = serv_acept(s, clients)
                srv_log.debug(f'All clients - {len(clients)}')
                read, write, error = select(clients, clients, [], wait)
                srv_log.debug(f'Write - {len(write)}')
                srv_log.debug(f'Read - {len(read)}')
                srv_log.debug(f'message_list - {message_list}')
                # srv_log.debug(
                #         f"Прошел селект \n"
                #         f'read - {read}\n'
                #         f'write - {write}\n')
            except Exception:
                # srv_log.debug('Exception под select', sys.exc_info()[0])
                pass

            if read:
                for s_client in read:
                    try:
                        data = get_message(s_client)
                        srv_log.info(f'Сообщение: {data} было отправлено клиентом: {s_client.getpeername()}')
                        msg = parsing_msg(data, s_client, message_list)
                    except Exception as e:
                        clients.remove(s_client)
                        srv_log.debug(sys.exc_info()[0])
                        srv_log.debug(f"Удалил клинета - {s_client}")

            if write:
                srv_log.debug(f'Отправляю клиентам')
                try:
                    for message in message_list:
                        send_dict = {
                                RESPONSE: 'message',
                                FROM: message[0],
                                MESSAGE_TEXT: message[1],
                            }
                        srv_log.debug(f'Формирую {send_dict}')
                        for s_client in write:
                            srv_log.debug(f'Отправляю {send_dict}')
                            send_message(send_dict, s_client)
                        message_list.remove(message)
                except Exception as e:
                    srv_log.debug(sys.exc_info()[0])
                    # raise
                    clients.remove(s_client)
                    srv_log.debug(f"Удалил клинета - {s_client}")


            # try:
            #     data = get_message(client)
            #     msg = parsing_msg(data)
            #     send_message(msg, client)
            #     srv_log.info(f'Закрываю соединение с {addr}')
            #     client.close()
            # except ConnectionResetError:
            #     srv_log.error('Произошла ошибка ConnectionResetError, закрываю соединение с клиентом')
            #     client.close()


if __name__ == '__main__':
    main()
