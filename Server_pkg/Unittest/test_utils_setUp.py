import os
import sys
import unittest
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

sys.path.append(os.path.join(os.getcwd(), '../..'))
from Server_pkg.common.variables import ANS_200, ACTION, TIME, USER, ACCOUNT_NAME, PASSWORD, ANS_400
from Server_pkg.common.utils import send_message, get_message


class TestUtilFunctionForSetUp(unittest.TestCase):
    """Тест функций отправки и получения сообщений с помощью метода SetUp"""

    def setUp(self) -> None:
        print("setUp")
        self.test_dict_send = {
            ACTION: 'presence',
            TIME: 1.1,
            USER: {
                ACCOUNT_NAME: 'guest',
                PASSWORD: ''
            }
        }
        self.servsocket = socket(AF_INET, SOCK_STREAM)
        self.servsocket.bind(('', 7777))
        self.servsocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.servsocket.listen(1)
        self.clientsocket = socket(AF_INET, SOCK_STREAM)
        self.clientsocket.connect(('127.0.0.1', 7777))
        send_message(self.test_dict_send, self.clientsocket)
        self.client, self.addr = self.servsocket.accept()

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

    def tearDown(self) -> None:
        print('tearDown')
        self.client.close()
        self.clientsocket.close()
        self.servsocket.close()
