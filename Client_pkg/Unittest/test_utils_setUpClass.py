import os
import sys
import unittest
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

sys.path.append(os.path.join(os.getcwd(), '../..'))
from Client_pkg.common.variables import ANS_200, ACTION, TIME, USER, ACCOUNT_NAME, PASSWORD, ANS_400
from Client_pkg.common.utils import send_message, get_message


class TestUtilFunctionForSetUpClass(unittest.TestCase):
    """Тест функций отправки и получения сообщений с помощью метода SetUp"""
    test_dict_send = {
        ACTION: 'presence',
        TIME: 1.1,
        USER: {
            ACCOUNT_NAME: 'guest',
            PASSWORD: ''
        }
    }
    servsocket = socket(AF_INET, SOCK_STREAM)
    servsocket.bind(('', 7777))
    servsocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    clientsocket = socket(AF_INET, SOCK_STREAM)
    servsocket.listen(1)
    clientsocket.connect(('127.0.0.1', 7777))
    send_message(test_dict_send, clientsocket)

    @classmethod
    def setUpClass(cls) -> None:
        print("setUpClass")
        cls.client, cls.addr = cls.servsocket.accept()

    def test_normal_get_server(self, ):
        """ Тест получения сообщения сервером"""
        print(f'test_normal_get_server')
        self.assertEqual(get_message(self.client), self.test_dict_send)

    def test_normal_send_server(self):
        """ Тест отправки сообщения сервером"""
        print(f'test_normal_send_server')
        self.assertEqual(send_message(ANS_200, self.client), 'Отправка успешна')

    def test_normal_send_client(self):
        """ Тест отправки сообщения клиентом"""
        print(f'test_normal_send_client')
        self.assertEqual(send_message(self.test_dict_send, self.clientsocket), 'Отправка успешна')

    def test_normal_get_client(self):
        """ Тест получения сообщения клиентом"""
        print(f'test_normal_get_client')
        send_message(ANS_400, self.client)
        self.assertEqual(get_message(self.clientsocket), ANS_400)

    @classmethod
    def tearDownClass(cls) -> None:
        print('tearDownClass')
        cls.client.close()
        cls.clientsocket.close()
        cls.servsocket.close()
