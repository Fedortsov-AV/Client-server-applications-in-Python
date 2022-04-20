import logging
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread

from PyQt5 import QtCore
import log.client_log_config
from client_db import MessageHistory, UserContact
from common.utils import send_message, get_message
from common.variables import PASSWORD, TIME, ACCOUNT_NAME, DEFAULT_PORT, DEFAULT_ADR, VALID_ADR, VALID_PORT, ALERT, \
    ACTION, USER, RESPONSE, MESSAGE_TEXT, FROM, CONTACT_NAME, ADD_CONTACT, DEL_CONTACT, USER_NAME, CONTACT
from decorator import logs
from meta import ClientVerifier

logger = logging.getLogger('client')


class UserClient(QtCore.QThread):
    info = QtCore.pyqtSignal(str)
    __metaclass__ = ClientVerifier
    msg = {}
    addres = str
    port = int
    user_name = USER_NAME
    contact_dict = dict
    list_contact = []
    running = False
    session = None
    socket = None

    @logs
    def presence_msg(self) -> dict:
        self.msg = {}
        self.msg = {
            ACTION: 'presence',
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.user_name,
                PASSWORD: ''
            }
        }
        logger.debug(f'сформировано сообщение {self.msg}')
        return self.msg

    @logs
    def generation_msg(self, message: str, name: str) -> dict:
        self.msg = {}
        if message.lower() == 'exit':
            self.msg = {
                ACTION: 'EXIT',
                TIME: time.time(),
                ACCOUNT_NAME: self.user_name,
            }
            logger.info('Закрываю скрипт')
        else:
            self.msg = {
                ACTION: 'MESSAGE',
                TIME: time.time(),
                ACCOUNT_NAME: self.user_name,
                MESSAGE_TEXT: message,
                FROM: name,
            }

        logger.debug(f'сформировано сообщение {self.msg}')
        return self.msg

    @logs
    def parsing_msg(self, input_date: dict):
        logger.debug(f'Получен аргумент {input_date}')
        try:
            if isinstance(input_date, dict):
                if input_date[RESPONSE] in (200, 202, 400) and input_date[ALERT] and input_date[TIME]:
                    if isinstance(input_date[TIME], float):
                        timeserv = time.strftime('%d.%m.%Y %H:%M', time.localtime(input_date[TIME]))
                        logger.info(f'{timeserv} - {input_date[RESPONSE]} : {input_date[ALERT]}')
                        if input_date[RESPONSE] == 202:
                            for i in input_date[CONTACT]:
                                self.list_contact.append(i)
                                result = self.session.query(UserContact).filter_by(contact=i)

                                if result.count() == 0:
                                    contact = UserContact(i)
                                    self.session.add(contact)
                                    self.session.commit()
                        self.info.emit("Соединение с сервером установлено")
                        return
                elif input_date[RESPONSE] in (104, 105) and input_date[ALERT] and input_date[TIME]:
                    if isinstance(input_date[TIME], float):
                        timeserv = time.strftime('%d.%m.%Y %H:%M', time.localtime(input_date[TIME]))
                        logger.info(f'{timeserv} - {input_date[RESPONSE]} : {input_date[ALERT]}')
                        sys.exit(0)

                elif input_date[RESPONSE] == 'message' and input_date[FROM] and input_date[MESSAGE_TEXT] and input_date[
                    ACCOUNT_NAME]:
                    item = MessageHistory(input_date[ACCOUNT_NAME], input_date[FROM], input_date[MESSAGE_TEXT])
                    self.session.add(item)
                    self.session.commit()
                    return f"{input_date[ACCOUNT_NAME]} написал: {input_date[MESSAGE_TEXT]}"
                raise ValueError
            raise TypeError
        finally:
            if sys.exc_info()[0] in (KeyError, TypeError, ValueError):
                logger.critical(f'Произошла ошибка {sys.exc_info()[0]}')
                return 'Неправильный ответ/JSON-объект'

    @logs
    def parse_addres_in_cmd(self, arg: list) -> str:
        # logger.debug(f'Получен аргумент {arg}')
        try:
            if isinstance(arg, list):
                if VALID_ADR.findall(arg[1]):
                    if VALID_ADR.findall(arg[1])[0]:
                        self.addres = VALID_ADR.findall(arg[1])[0]
                        logger.info(f'Установлен ip-адрес {self.addres}')
                        return self.addres
                    raise ValueError
                raise IndexError
            raise TypeError
        finally:
            if sys.exc_info()[0] in (IndexError, TypeError, ValueError):
                self.addres = DEFAULT_ADR
                logger.critical(f'Произошла ошибка {sys.exc_info()[0]}, установлен ip-адрес {self.addres}')
                return self.addres

    @logs
    def parse_port_in_cmd(self, arg: list) -> int:
        logger.debug(f'Получен аргумент {arg}')
        try:
            if isinstance(arg, list):
                if VALID_PORT.findall(arg[2]):
                    if VALID_PORT.findall(arg[2])[0]:
                        self.port = int(VALID_PORT.findall(arg[2])[0])
                        if 1024 < self.port < 65535:
                            logger.info(f'Установлен порт {self.port}')
                            return self.port
                        raise ValueError
                    raise IndexError
                raise IndexError
            raise TypeError
        finally:
            if sys.exc_info()[0] in (IndexError, TypeError, ValueError):
                self.port = int(DEFAULT_PORT)
                logger.critical(f'Произошла ошибка {sys.exc_info()[0]}, установлен порт {self.port}')
                return self.port

    def get_server_msg(self) -> None:
        logger.debug('Жду данные от сервера')

        while True:
            data = get_message(self.socket)
            logger.debug('Разбираю ответ сервера')
            print(self.parsing_msg(data))

    def send_msg(self, text: str, name: str) -> None:
        # item_message = MessageHistory(self.user_name, name, text)
        # self.session.add(item_message)
        # self.session.commit()
        message = self.generation_msg(text, name)
        logger.debug('Отправляю сообщение на сервер')
        send_message(message, self.socket)
        if message[ACTION] != 'EXIT':
            user_msg = MessageHistory(message[ACCOUNT_NAME], message[FROM], message[MESSAGE_TEXT])
            self.session.add(user_msg)
            self.session.commit()
        if message[ACTION] == 'EXIT':
            self.socket = None
            time.sleep(0.7)

    def add_contact(self, contact_name: str) -> None:
        self.msg = {
            ACTION: ADD_CONTACT,
            CONTACT_NAME: contact_name,
            TIME: time.time(),
            ACCOUNT_NAME: self.user_name,
        }

        return send_message(self.msg, self.socket)

    def del_contact(self, contact_name: str):
        self.msg = {
            ACTION: DEL_CONTACT,
            CONTACT_NAME: contact_name,
            TIME: time.time(),
            ACCOUNT_NAME: self.user_name,
        }
        cont = self.session.query(UserContact).filter_by(contact=contact_name)
        cont.delete()
        self.session.commit()
        return send_message(self.msg, self.socket)

    def init_socket(self):
        clientsock = socket(AF_INET, SOCK_STREAM)
        self.running = True
        return clientsock

    def run(self):
        # self.parse_addres_in_cmd(sys.argv)
        # self.parse_port_in_cmd(sys.argv)
        # self.init_bd_session()
        self.socket = self.init_socket()
        self.running = True
        logger.info(f'Сокет будет привязан к  {(self.addres, self.port)}')

        self.socket.connect((self.addres, self.port))
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        pres = self.presence_msg()
        send_message(pres, self.socket)
        self.parsing_msg(get_message(self.socket))
        self.parsing_msg(get_message(self.socket))
        get = Thread(target=self.get_server_msg, daemon=True, name='get')
        # send = Thread(target=self.send_msg, args=(clientsock,), daemon=True, name='send')
        get.start()
        # send.start()

        while self.running:
            time.sleep(1)
            if get.is_alive():
                continue

            self.socket.close()
            break


def main():
    client = UserClient()
    client.user_name = input('Введите ваше имя: ')

    # print('Main session ', session)

    client.run_client()


if __name__ == '__main__':
    main()
