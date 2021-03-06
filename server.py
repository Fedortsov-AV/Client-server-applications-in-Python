import logging
import sys
import time
from select import select
from socket import socket, AF_INET, SOCK_STREAM

from PyQt5 import QtCore

from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, VALID_ADR, VALID_PORT, ANS_200, ANS_400, ACTION, USER, TIME, ACCOUNT_NAME, \
    MESSAGE_TEXT, FROM, RESPONSE, ALERT, CONTACT_NAME, ADD_CONTACT, DEL_CONTACT, ANS_202, CONTACT
from decorator import logs
from descriptor import SocketPort
from meta import ServerVerifier
from server_db import User, UserContact, UserHistory
import log.server_log_config

srv_log = logging.getLogger('server')


class Server(QtCore.QThread):
    __metaclass__ = ServerVerifier
    finish = QtCore.pyqtSignal(str)
    ADDRES = str
    PORT = SocketPort()
    clients = []
    message_list = []
    clients_dict = dict()
    session = None
    running = False

    @logs
    def parsing_msg(self, input_date: dict, sock: socket) -> None:
        srv_log.info(f'Получен аргумент: {input_date}')
        try:
            if isinstance(input_date, dict):
                if input_date[ACTION] == 'presence' and input_date[USER][ACCOUNT_NAME] != '' and input_date[TIME]:
                    self.response_user(input_date[USER][ACCOUNT_NAME], sock.getpeername()[0])
                    ANS_200[ALERT] = "OK"
                    send_message(ANS_200, sock)
                    self.clients_dict[input_date[USER][ACCOUNT_NAME]] = sock
                    ANS_202[CONTACT] = self.contact_list(input_date[USER][ACCOUNT_NAME])
                    ANS_202[ALERT] = "Отправлен список контактов"
                    print(ANS_202[CONTACT])
                    srv_log.debug(f'Сообщение клиента соответствует требованиям, отвечаю {ANS_200}')
                    send_message(ANS_202, sock)
                    self.finish.emit(f'Отправлен список контактов {input_date[USER][ACCOUNT_NAME]}')
                    return
                elif input_date[ACTION] == 'MESSAGE' and input_date[ACCOUNT_NAME] and input_date[MESSAGE_TEXT] \
                        and input_date[FROM] != '':
                    self.message_list.append([input_date[ACCOUNT_NAME], input_date[FROM], input_date[MESSAGE_TEXT]])
                    return
                elif input_date[ACTION] == 'EXIT' and input_date[ACCOUNT_NAME]:
                    result = self.session.query(User).filter_by(username=input_date[ACCOUNT_NAME])
                    result.first().online = 0
                    self.session.commit()
                    self.clients_dict.remove(input_date[ACCOUNT_NAME])
                    srv_log.debug(f"Удалил клиента - {input_date[ACCOUNT_NAME]}")
                    self.finish.emit(f'Удалил клиента - {input_date[ACCOUNT_NAME]}')
                    return
                elif input_date[ACTION] == ALERT and input_date[RESPONSE] in (104, 105):
                    timeserv = time.strftime('%d.%m.%Y %H:%M', time.localtime(input_date[TIME]))
                    srv_log.info(f'{timeserv} - {input_date[RESPONSE]} : {input_date[ALERT]}')
                    self.clients.remove(sock)
                    return
                elif input_date[ACTION] == ADD_CONTACT and input_date[CONTACT_NAME] and input_date[ACCOUNT_NAME]:
                    if not self.add_contact(input_date[ACCOUNT_NAME], input_date[CONTACT_NAME]):
                        ANS_200[ALERT] = 'Не удалось добавить контакт'
                        send_message(ANS_200, sock)
                        return
                    ANS_202[ALERT] = 'Контакт успешно добавлен'
                    self.finish.emit(f'Добавлен контакт {input_date[CONTACT_NAME]}  для клиента - {input_date[ACCOUNT_NAME]}')
                    ANS_202[CONTACT] = [input_date[CONTACT_NAME]]
                    send_message(ANS_202, sock)
                    return
                elif input_date[ACTION] == DEL_CONTACT and input_date[CONTACT_NAME] and input_date[ACCOUNT_NAME]:
                    if not self.delete_contact(input_date[ACCOUNT_NAME], input_date[CONTACT_NAME]):
                        ANS_202[ALERT] = 'Не удалось найти/удалить контакт'
                        send_message(ANS_202, sock)
                        return
                    ANS_200[ALERT] = 'Контакт успешно удален'
                    send_message(ANS_200, sock)
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
                srv_log.info(f'Установлен адрес: {self.ADDRES}')
                return self.ADDRES

    @logs
    def parse_port_in_argv(self, arg: list):
        # srv_log.debug(f'Получен аргумент: {arg}')
        try:
            if isinstance(arg, list):
                if '-p' in arg:
                    # self.PORT = 77.7
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
                srv_log.info(f'Установлен порт: {self.PORT}')
                return self.PORT

    def run_socket(self):
        if self.running == False:
            s = socket(AF_INET, SOCK_STREAM)
            self.running = True
            return s

    def run(self):
        # self.parse_addres_in_argv(sys.argv)
        # self.parse_port_in_argv(sys.argv)
        with self.run_socket() as s:
            s.settimeout(0.5)
            srv_log.info(f'Сокет будет привязан к  {(self.ADDRES, self.PORT)}')
            s.bind((self.ADDRES, self.PORT))
            s.listen(5)
            self.clients = []
            self.message_list = []
            while self.running:
                # print(self.running)
                wait = 0
                write = []
                read = []
                try:
                    try:
                        client, addr = s.accept()
                    except OSError as e:
                        pass
                        # srv_log.debug(f"Ошибка {e}")
                    else:
                        srv_log.info(f"Запрос на соединение от {addr}")
                        self.clients.append(client)
                    read, write, error = select(self.clients, self.clients, [], wait)
                    srv_log.debug(f'Write - {len(write)}')
                    srv_log.debug(f'Read - {len(read)}')
                    srv_log.debug(f'message_list - {self.message_list}')
                except Exception:
                    pass

                if read:
                    for s_client in read:
                        try:
                            data = get_message(s_client)
                            srv_log.info(f'Сообщение: {data} было отправлено клиентом: {s_client.getpeername()}')

                            msg = self.parsing_msg(data, s_client)
                        except Exception as e:
                            self.clients.remove(s_client)
                            srv_log.debug(f'Ошибка при получении - {sys.exc_info()[0]}')
                            srv_log.debug(f"Удалил клиента - {s_client}")

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
                                # srv_log.info(sys.exc_info()[0])
                                srv_log.debug(f'Отправляю {send_dict}')
                                self.message_list.remove(message)
                    except Exception as e:
                        srv_log.info(sys.exc_info()[0])
                        # raise
                        self.clients.remove(s_client)
                        del self.clients_dict[message[0]]
                        srv_log.debug(f"Удалил клиента - {s_client}")
            # print('Закрываю сокет')
            srv_log.info(f"Закрываю сокет")
            s.close()
            srv_log.info(f"Сокет закрыт")





    def add_contact(self, username: str, user_contact: str) -> bool:
        try:
            user = self.session.query(User).filter_by(username=username)
            verify_cont = self.session.query(UserContact).filter_by(user_id=user[0].id, contact=user_contact)
            if verify_cont.count() == 0:
                contact = self.session.query(User).filter_by(username=user_contact)
                data = UserContact(user[0].id, contact[0].username)
                self.session.add(data)
                self.session.commit()

                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def delete_contact(self, username: str, user_contact: str) -> bool:
        user = self.session.query(User).filter_by(username=username).first()
        contact = self.session.query(UserContact).filter_by(user_id=user.id, contact=user_contact)
        try:
            if contact.count() > 0:
                contact.delete()
                self.session.commit()
                return True
            return False
        except Exception as e:
            print(e)
            return False



    def response_user(self, username: str, ip: str) -> None:
        result = self.session.query(User).filter_by(username=username)
        if result.count() == 0:
            user = User(username, "")
            self.session.add(user)
            self.session.commit()
        user_history = UserHistory(result.first().id, ip, result.first().username)
        self.session.add(user_history)
        result.first().online = 1
        self.session.commit()

    def contact_list(self, name: str) -> list:
        user = self.session.query(User).filter_by(username=name)
        list = self.session.query(UserContact).filter_by(user_id=user[0].id)
        list_contact = []
        for set in list.all():
            list_contact.append(set.contact)
        return list_contact


def main():
    server = Server()
    server.run_server()


if __name__ == '__main__':
    main()
