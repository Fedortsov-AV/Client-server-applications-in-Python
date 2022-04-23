import binascii
import hashlib
import logging
import random
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox

import log.client_log_config
from client_db import MessageHistory, UserContact
from common.utils import send_message, get_message
from common.variables import PASSWORD, TIME, ACCOUNT_NAME, DEFAULT_PORT, DEFAULT_ADR, VALID_ADR, VALID_PORT, ALERT, \
    ACTION, USER, RESPONSE, MESSAGE_TEXT, FROM, CONTACT_NAME, ADD_CONTACT, DEL_CONTACT, USER_NAME, CONTACT, AUTH, REG, \
    OPEN_KEY_Y, OPEN_KEY_G, OPEN_KEY_P, SESSION_KEY
from decorator import logs
from meta import ClientVerifier

logger = logging.getLogger('client')


class UserClient(QtCore.QThread):
    info = QtCore.pyqtSignal(str)
    messeg_client = QtCore.pyqtSignal(str)
    __metaclass__ = ClientVerifier
    msg = {}
    addres = str
    port = int
    user_name = USER_NAME
    _password = str
    contact_dict = dict
    running = False
    session = None
    socket = None
    get = None

    @logs
    def presence_msg(self) -> dict:
        self.msg = {}
        dk = hashlib.pbkdf2_hmac('sha256', self._password.encode('UTF-8'), b'UserClient', 100000)
        print(binascii.hexlify(dk))

        self.msg = {
            ACTION: 'presence',
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.user_name,
                PASSWORD: binascii.hexlify(dk).decode('UTF-8')
            }
        }
        logger.debug(f'сформировано сообщение {self.msg}')
        return self.msg

    @logs
    def generation_msg(self, message: str, name: str) -> dict:
        self.msg = {}
        contact = self.session.query(UserContact).filter_by(contact=name)
        encrypt_msg, a =self.encrypt(
            message,
            int(contact.first().open_key_p),
            int(contact.first().open_key_y),
            int(contact.first().open_key_g),
        )

        self.msg = {
            ACTION: 'MESSAGE',
            TIME: time.time(),
            ACCOUNT_NAME: self.user_name,
            MESSAGE_TEXT: encrypt_msg,
            SESSION_KEY: a,
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
                        if input_date[RESPONSE] == 200 and input_date[ALERT] == "Недопустимая пара логин/пароль":
                            self.running = False
                            return self.messeg_client.emit(input_date[ALERT])
                        elif input_date[RESPONSE] == 200 and input_date[ALERT] in ["Вход выполнен", "Регистрация успешна", 'Контакт успешно добавлен', 'Не удалось добавить контакт']:
                            if input_date[ALERT] == "Вход выполнен":
                                with open(f"common/secret_key_{self.user_name}", "r") as f:
                                    self.key = int(f.readline())
                                    self.y = int(f.readline())
                                    self.g = int(f.readline())
                                    self.p = int(f.readline())
                            return self.messeg_client.emit(input_date[ALERT])

                        elif input_date[RESPONSE] == 202:
                            while not self.session:
                                time.sleep(0.5)
                            for i in input_date[CONTACT]:
                                result = self.session.query(UserContact).filter_by(contact=i)
                                if result.count() == 0:
                                    contact = UserContact(i,
                                                          str(input_date[CONTACT][i][0]),
                                                          str(input_date[CONTACT][i][1]),
                                                          str(input_date[CONTACT][i][2])
                                                          )
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
                    print(input_date)
                    text = self.decrypt(input_date[MESSAGE_TEXT], int(input_date[SESSION_KEY]), self.key, self.p)

                    item = MessageHistory(input_date[ACCOUNT_NAME], input_date[FROM], text)
                    self.session.add(item)
                    self.session.commit()
                    return f"{input_date[ACCOUNT_NAME]} написал: {text}"
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
        print(f'self.socket in get_server_msg - {self.socket}')
        try:
            while True:
                data = get_message(self.socket)
                logger.debug('Разбираю ответ сервера')
                print(self.parsing_msg(data))
        except Exception as e:
            print(f'in get_server_msg - {e}')

    def send_msg(self, text: str, name: str) -> None:
        message = self.generation_msg(text, name)
        logger.debug('Отправляю сообщение на сервер')
        send_message(message, self.socket)
        user_msg = MessageHistory(message[ACCOUNT_NAME], message[FROM], text)
        self.session.add(user_msg)
        self.session.commit()

    def exit_msg(self) -> None:
        self.msg = {}
        self.msg = {
            ACTION: 'EXIT',
            TIME: time.time(),
            ACCOUNT_NAME: self.user_name,
        }
        logger.info('Закрываю скрипт')
        send_message(self.msg, self.socket)
        time.sleep(0.7)
        self.running = False

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



    def authentication(self):
        """
        Метод формирует от отправляет сообщение для авторизации
        на сервере
        """
        pres = self.presence_msg()
        send_message(pres, self.socket)

    def registration(self):
        """
        Метод создает ключи шифрования, формирует и отправляет сообщение на
        сервер о необходимости зарегистрировать пользователя
        """
        self.generator_asinc_key()
        self.msg = {}
        dk = hashlib.pbkdf2_hmac('sha256', self._password.encode('UTF-8'), b'UserClient', 100000)
        print(binascii.hexlify(dk))
        self.msg = {
            ACTION: REG,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.user_name,
                PASSWORD: binascii.hexlify(dk).decode('UTF-8'),
                OPEN_KEY_Y: self.y.__str__(),
                OPEN_KEY_G: self.g.__str__(),
                OPEN_KEY_P: self.p.__str__()
            }
        }
        try:
            send_message(self.msg, self.socket)
        except Exception as e:
            print(f'registration - {e}')

    def run(self):
        self.socket = self.init_socket()
        self.running = True
        try:
            logger.info(f'Сокет будет привязан к  {(self.addres, self.port)}')
            self.socket.connect((self.addres, self.port))
            self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        except ConnectionRefusedError:
            self.running = False
            self.socket.close()
            self.messeg_client.emit(str(sys.exc_info()[1]))

        else:
            self.get = Thread(target=self.get_server_msg, daemon=False, name='get')
            self.get.start()


            while self.running:
                time.sleep(1)
                if self.get.is_alive():
                    continue
                break
            print('Закрываю сокет')
            self.socket.close()

    def gsd(self, a, b):
        if a < b:
            return self.gsd(b, a)
        elif a % b == 0:
            return b
        else:
            return self.gsd(b, a % b)

    def generation_key(self, q):

        key = random.randint(pow(10, 20), q)

        while self.gsd(q, key) != 1:
            key = random.randint(pow(10, 20), q)

        return key

    def power(self, a, b, c):
        x = 1
        y = a

        while b > 0:
            if b % 2 == 0:
                x = (x * y) % c
            y = (y * y) % c
            b = int(b / 2)

        return x % c

    def encrypt(self, msg: str, p: int, y: int, g: int) -> list and int:
        """
        Для шифрования каждого отдельного блока исходного сообщения должно выбираться случайное число k (1 < k < p – 1).
        После чего шифрограмма генерируется по следующим формулам
        a = g^k mod p,
        b = (y^k*Т) mod p,
        где Т – исходное сообщение;
        (a, b) – зашифрованное сообщение.
        :param msg:
        :param q:
        :param h:
        :param g:
        :return:
        """


        k = self.generation_key(p)
        s = self.power(y, k, p)
        # Блок "p" отдать пользователю вместе с зашифрованным сообщением!
        a = self.power(g, k, p)
        en_msg = [ord(_) * s for _ in msg]

        return en_msg, a

    def decrypt(self, en_msg: list, a: int, key: int, p: int) -> str:
        """
        Дешифрование сообщения выполняется по следующей формуле
        T = (b (a^x)^-1) mod p
        или
        T = (b*a^(p-1-x)) mod p,
        где (a^x)^-1 – обратное значение числа a^x по модулю p.
        :param en_msg:
        :param p:
        :param key:
        :param q:
        :return:
        """
        dr_msg = ''
        h = self.power(a, key, p)

        for _ in en_msg:
            dr_msg = dr_msg + chr(int(_ / h))
        return dr_msg



    def generator_asinc_key(self):
        """
        1	Выбирается простое число p.
        2	Выбирается число g (0 < g < p), являющееся первообразным корнем по модулю p*)
        3	Выбирается закрытый ключ x (дискретный логарифм) - произвольное натуральное число (0 < x < p)
        4	Вычисляется y = g^x mod p.
        Открытый ключ (y, g, p) - отправляется серверу для привязки к пользователю
        self.key  - Приватный ключ, остается только у пользователя
        """

        self.p = random.randint(pow(10, 20), pow(10, 50))

        # генерация приватного ключа (X)
        self.key = self.generation_key(self.p)  # Privat key

        # второй блок открытого ключа
        self.g = random.randint(2, self.p)


        # первый блок открытого ключа
        self.y = self.power(self.g, self.key, self.p)


        # Открытый ключ (y, g, p)
        self.open_key = (self.y, self.g, self.p)

        # Записываем в файл для данного пользователя оба ключа
        with open(f"common/secret_key_{self.user_name}", "w") as f:
            # В первую строку записываем секретный ключ
            f.writelines(f"{self.key}\n")
            # Во вторую строку записываем первый блок открытого ключа
            f.writelines(f"{self.open_key[0]}\n")
            # В третию строку записываем второй блок открытого ключа
            f.writelines(f"{self.open_key[1]}\n")
            # В четвертую строку записываем третий блок открытого ключа
            f.writelines(f"{self.open_key[2]}\n")
        encrypt_msg, a = self.encrypt('Тест шифровки', self.p, self.y, self.g)

        print(f'Тест шифровки = {encrypt_msg}')

        decript_msg = self.decrypt(encrypt_msg, a, self.key, self.p)

        print(f'Тест расшифровки = {decript_msg}')










def main():
    client = UserClient()
    client.generator_asinc_key()
    # client.user_name = input('Введите ваше имя: ')
    #
    # # print('Main session ', session)
    #
    # client.run_client()


if __name__ == '__main__':
    main()
