import os
import sys
import time
import unittest
from unittest.mock import patch

sys.path.append(os.path.join(os.getcwd(), '..'))
from server import parsing_msg, parse_addres_in_argv, parse_port_in_argv
from common.variables import ANS_200, ANS_400, ACTION, USER, TIME, AUTH_USER, PASSWORD, VALID_ADR, VALID_PORT


class TestServerParsingMsg(unittest.TestCase):
    """Тестирование функции parsing_msg сервера"""
    test_list = [1, 2, 3]
    test_tuple = (1, 2, 3)
    test_dict = {
        ACTION: 'presence',
        TIME: time.time(),
        USER: {
            AUTH_USER: 'guest',
            PASSWORD: ''
        }
    }
    test_error_dict = {
        ACTION: 'prsence',
        USER: {
            AUTH_USER: 'guest',
            PASSWORD: ''
        }
    }

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @unittest.skip
    def testKeyError(self):
        """
        Проверка KeyError (Пропускается-тест должен вернуть fail)
        """
        self.assertRaises(KeyError, parsing_msg, self.test_error_dict)

    @unittest.skip
    def testValueError(self):
        """
        Проверка ValueError (Пропускается-тест должен вернуть fail)
        """
        self.assertRaises(ValueError, parsing_msg, self.test_error_dict)

    @unittest.skip
    def testTypeErrorr(self):
        """
        Проверка TypeError(Пропускапется-тест должен вернуть fail)
        """
        self.assertRaises(TypeError, parsing_msg, self.test_list)

    def test_true_data(self):
        """Проверка корректного presence-сообщеня"""
        self.assertEqual(parsing_msg(self.test_dict), ANS_200)

    def test_fail_data(self):
        """Проверка ошибки ключа действия"""
        self.assertEqual(parsing_msg({ACTION: 'prsence', USER: 'guest'}), ANS_400)

    def test_no_key_user(self):
        """Проверка отсутствия ключа 'USER'"""
        self.assertEqual(parsing_msg({ACTION: 'prsence'}), ANS_400)

    def test_no_key_action(self):
        """Проверка отсутствия ключа 'ACTION'"""
        self.assertEqual(parsing_msg({USER: 'guest'}), ANS_400)

    def test_data_no_dict(self):
        """Проверка неверного типа данных аргумента функции"""
        self.assertEqual(parsing_msg(self.test_list), ANS_400)

    def test_date_none(self):
        """Проверка передачи пустого словаря в агрумент"""
        self.assertEqual(parsing_msg({}), ANS_400)


class TestServerparseAddressInArgv(unittest.TestCase):
    """Тестирование функции parse_address_in_argv сервера"""

    @patch.object(sys, 'argv', ['server.py', '-a', '127.0.0.1'])
    def test_normal(self):
        """ Проверяем вывод функции при нормальном задании адреса"""
        self.assertEqual(parse_addres_in_argv(['server.py', '-a', '127.0.0.1']), '127.0.0.1')

    @patch.object(sys, 'argv', ['server.py'])
    def test_defult_addres(self):
        """ Проверяем вывод функции при отсутствии задании адреса в командной строке"""
        self.assertEqual(parse_addres_in_argv(sys.argv), '')

    @patch.object(sys, 'argv', ['server.py', '-a', '12777777.0.0.1'])
    def test_no_corre_addres(self):
        """ Проверяем вывод функции при ошибочном задании адреса"""
        self.assertEqual(parse_addres_in_argv(sys.argv), '')

    @patch.object(sys, 'argv', ['server.py', '-a:', '127.0.0.1'])
    def test_no_correct_addres(self):
        """ Проверяем вывод функции при ошибочном задании адреса"""
        self.assertEqual(parse_addres_in_argv(sys.argv), '')

    @patch.object(sys, 'argv', ['server.py', '-a', '127.0.0.1'])
    def test_true_patern_addres(self):
        """Проверка корректного ip-адреса в командной строке"""
        self.assertRegex(parse_addres_in_argv(sys.argv), VALID_ADR)

    @patch.object(sys, 'argv', ['server.py', '-a', '1277.0.7770.1'])
    def test_fails_patern_addres(self):
        """Проверка не корректного ip-адреса в командной строке"""
        self.assertNotRegex(parse_addres_in_argv(sys.argv), VALID_ADR)

    @patch.object(sys, 'argv', ['server.py', '127.0.0.1'])
    def test_no_correct_addres1(self):
        """ Проверяем вывод функции при ошибочном задании адреса"""
        self.assertEqual(parse_addres_in_argv(sys.argv), '')

    @unittest.skip
    def test_IndexError(self):
        """ Проверка IndexError (Пропускается-тест должен вернуть fail)"""
        self.assertRaises(IndexError, parse_addres_in_argv, sys.argv)

    @unittest.skip
    def test_TypeError(self):
        """ Проверка TypeError (Пропускается-тест должен вернуть fail)"""
        self.assertRaises(TypeError, parse_addres_in_argv, (1, 2, 3))

    @unittest.skip
    def test_ValueError(self):
        """ Проверка ValueError (Пропускается-тест должен вернуть fail)"""
        self.assertRaises(ValueError, parse_addres_in_argv, ['server.py', '-a'])


class TestServerParsePortInArgv(unittest.TestCase):
    """Тестирование функции parse_port_in_argv сервера"""

    @patch.object(sys, 'argv', ['server.py', '-a', '127.0.0.1', '-p', 7777])
    def test_normal(self):
        """ Проверяем вывод функции при нормальном задании порта"""
        self.assertEqual(parse_port_in_argv(sys.argv), 7777)

    @patch.object(sys, 'argv', ['server.py'])
    def test_defult_port(self):
        """ Проверяем вывод функции при отсутствии задании порта в командной строке"""
        self.assertEqual(parse_port_in_argv(sys.argv), 7777)

    @patch.object(sys, 'argv', ['server.py', '-a', '127.0.0.1', '-p', 887777])
    def test_no_corre_port(self):
        """ Проверяем вывод функции при ошибочном задании порта"""
        self.assertEqual(parse_port_in_argv(sys.argv), 7777)

    @patch.object(sys, 'argv', ['server.py', '-a', '127.0.0.1', '-p:', 7777])
    def test_no_correct_port(self):
        """ Проверяем вывод функции при ошибочном задании порта"""
        self.assertEqual(parse_port_in_argv(sys.argv), 7777)

    @patch.object(sys, 'argv', ['server.py', '-a', '127.0.0.1', '-p', 7777])
    def test_true_patern_port(self):
        """Проверка корректного порта в командной строке по маске"""
        self.assertRegex(str(parse_port_in_argv(sys.argv)), VALID_PORT)

    @patch.object(sys, 'argv', ['server.py', '-a', '127.0.0.1', 7777])
    def test_no_correct_port1(self):
        """ Проверяем вывод функции при ошибочном задании порта"""
        self.assertEqual(parse_port_in_argv(sys.argv), 7777)

    @unittest.skip
    def test_IndexError(self):
        """ Проверка IndexError (Пропускается-тест должен вернуть fail)"""
        self.assertRaises(IndexError, parse_port_in_argv, sys.argv)

    @unittest.skip
    def test_TypeError(self):
        """ Проверка TypeError (Пропускается-тест должен вернуть fail)"""
        self.assertRaises(TypeError, parse_port_in_argv, (1, 2, 3))

    @unittest.skip
    def test_ValueError(self):
        """ Проверка ValueError (Пропускается-тест должен вернуть fail)"""
        self.assertRaises(ValueError, parse_port_in_argv, ['server.py', '-p'])


if __name__ == '__main__':
    unittest.main()
