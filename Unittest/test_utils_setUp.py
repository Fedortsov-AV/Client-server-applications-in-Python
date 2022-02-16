import os
import sys
import unittest
from socket import socket, AF_INET, SOCK_STREAM

from common.variables import ANS_200, DEFAULT_PORT, DEFAULT_ADR, ACTION, TIME, USER, ACCOUNT_NAME, PASSWORD, ANS_400

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.utils import send_message, get_message

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
        self.servsocket.bind(('', DEFAULT_PORT))
        self.servsocket.listen(1)
        self.clientsocket = socket(AF_INET, SOCK_STREAM)
        self.clientsocket.connect((DEFAULT_ADR, DEFAULT_PORT))
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