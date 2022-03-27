import logging
import sys
import time
from select import select
from socket import socket, AF_INET, SOCK_STREAM

from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, VALID_ADR, VALID_PORT, ANS_200, ANS_400, ACTION, USER, TIME, ACCOUNT_NAME, \
    MESSAGE_TEXT, FROM, RESPONSE, ALERT
from decorator import logs
import log.server_log_config

srv_log = logging.getLogger('server')

class Server():
    ADDRES = str
    PORT = int
    clients = []
    message_list = []
    clients_dict = dict()


    @logs
    def parsing_msg(self, input_date: dict, sock: socket, message_list: list, clients: list):
        # srv_log.debug(f'Получен аргумент: {input_date}')
        try:
            if isinstance(input_date, dict):
                if input_date[ACTION] == 'presence' and input_date[USER][ACCOUNT_NAME] != '' and input_date[TIME]:
                    self.clients_dict[input_date[USER][ACCOUNT_NAME]] = sock
                    srv_log.debug(f'Сообщение клиента соответствует требованиям, отвечаю {ANS_200}')
                    return send_message(ANS_200, sock)
                elif input_date[ACTION] == 'MESSAGE' and input_date[ACCOUNT_NAME] and input_date[MESSAGE_TEXT] \
                        and input_date[FROM] != '':
                    message_list.append([input_date[ACCOUNT_NAME], input_date[FROM], input_date[MESSAGE_TEXT]])
                    return message_list
                elif input_date[ACTION] == 'EXIT' and input_date[ACCOUNT_NAME]:
                    self.clients_dict.remove(input_date[ACCOUNT_NAME])
                    srv_log.debug(f"Удалил клинета - {input_date[ACCOUNT_NAME]}")
                    return
                elif input_date[ACTION] == ALERT and input_date[RESPONSE] in (104, 105):
                    timeserv = time.strftime('%d.%m.%Y %H:%M', time.localtime(input_date[TIME]))
                    srv_log.info(f'{timeserv} - {input_date[RESPONSE]} : {input_date[ALERT]}')
                    clients.remove(sock)
                    return

                raise KeyError
            raise TypeError
        finally:
            if sys.exc_info()[0] in (KeyError, TypeError, ValueError):
                srv_log.critical(f'Произошла ошибка: {sys.exc_info()[0]}')
                return send_message(ANS_400, sock)


    @logs
    def parse_addres_in_argv(self, arg: list):
        # srv_log.debug(f'Получен аргумент: {arg}')
        try:
            if isinstance(arg, list):
                if '-a' in arg:
                    if VALID_ADR.findall(arg[sys.argv.index('-a') + 1]):
                        if VALID_ADR.findall(arg[arg.index('-a') + 1])[0]:
                            self.ADDRES = VALID_ADR.findall(arg[arg.index('-a') + 1])[0]
                            srv_log.debug(f'В командной строке задан ip-адрес: {self.ADDRES}')
                            return self.ADDRES
                        raise ValueError
                    raise IndexError
                raise IndexError
            raise TypeError
        finally:
            if sys.exc_info()[0] in (IndexError, TypeError, ValueError):
                self.ADDRES = ''
                srv_log.warning(f'Установлен адрес: {self.ADDRES}')
                return self.ADDRES


    @logs
    def parse_port_in_argv(self, arg: list):
        # srv_log.debug(f'Получен аргумент: {arg}')
        try:
            if isinstance(arg, list):
                if '-p' in arg:
                    if VALID_PORT.findall(arg[sys.argv.index('-p') + 1]):
                        if VALID_PORT.findall(arg[arg.index('-p') + 1])[0]:
                            self.PORT = int(VALID_PORT.findall(arg[arg.index('-p') + 1])[0])
                            if self.PORT > 1024 or self.PORT < 65535:
                                self.PORT = int(DEFAULT_PORT)
                                srv_log.debug(f'В командной строке задан порт: {self.PORT}')
                                return self.PORT
                            raise ValueError
                        raise ValueError
                    raise IndexError
                raise IndexError
            raise TypeError
        finally:
            if sys.exc_info()[0] in (IndexError, TypeError, ValueError):
                self.PORT = int(DEFAULT_PORT)
                srv_log.warning(f'Установлен порт: {self.PORT}')
                return self.PORT


    def serv_acept(self, s: socket, clients: list):
        try:
            client, addr = s.accept()
        except OSError as e:
            # srv_log.debug(f"Ошибка {e}")
            return self.clients
        else:
            srv_log.info(f"Запрос на соединение от {addr}")
            self.clients.append(client)
            return self.clients

    def run_server(self):
        self.parse_addres_in_argv(sys.argv)
        self.parse_port_in_argv(sys.argv)
        srv_log.info(f'Сокет будет привязан к  {(self.ADDRES, self.PORT)}')
        with socket(AF_INET, SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.bind((self.ADDRES, self.PORT))
            s.listen(5)
            self.clients = []
            self.message_list = []
            while True:
                # finally:
                wait = 0
                write = []
                read = []
                try:
                    self.clients = self.serv_acept(s, self.clients)
                    srv_log.debug(f'All clients - {len(self.clients)}')
                    read, write, error = select(self.clients, self.clients, [], wait)
                    srv_log.debug(f'Write - {len(write)}')
                    srv_log.debug(f'Read - {len(read)}')
                    srv_log.debug(f'message_list - {self.message_list}')
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
                            msg = self.parsing_msg(data, s_client, self.message_list, self.clients)
                        except Exception as e:
                            self.clients.remove(s_client)
                            srv_log.debug(f'Ошибка при получении - {sys.exc_info()[0]}')
                            srv_log.debug(f"Удалил клинета - {s_client}")

                if write:
                    srv_log.debug(f'Отправляю клиенту')
                    try:

                        for message in self.message_list:
                            if message[1] in self.clients_dict:
                                send_dict = {}
                                send_dict = {
                                    RESPONSE: 'message',
                                    ACCOUNT_NAME: message[0],
                                    FROM: message[1],
                                    MESSAGE_TEXT: message[2],
                                }
                                srv_log.debug(f'Формирую {send_dict}')
                                print(self.clients_dict[message[1]])
                                send_message(send_dict, self.clients_dict[message[1]])
                                srv_log.info(sys.exc_info()[0])
                                srv_log.debug(f'Отправляю {send_dict}')
                                self.message_list.remove(message)
                            # message_list.remove(message)
                    except Exception as e:
                        srv_log.info(sys.exc_info()[0])
                        # raise
                        self.clients.remove(s_client)
                        del self.clients_dict[message[0]]
                        srv_log.debug(f"Удалил клинета - {s_client}")


def main():
    server = Server()
    server.run_server()



if __name__ == '__main__':

    main()
