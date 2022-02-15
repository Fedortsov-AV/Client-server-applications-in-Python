import os
import sys
import time
import unittest
from unittest.mock import patch

sys.path.append(os.path.join(os.getcwd(), '..'))
from server import parcing_msg, parse_adress_in_argv, parse_port_in_argv
from common.variables import ANS_200, ANS_400, ACTION, USER, TIME, AUTHUSER, PASSWORD, VALID_ADR, VALID_PORT


class TestServerpParcing_msg(unittest.TestCase):
    '''
        Тестирование функций сервера
    '''
    testlist = [1, 2, 3]
    testtuple = (1, 2, 3)
    testdict = {
        ACTION: 'presence',
        TIME: time.time(),
        USER: {
            AUTHUSER: 'guest',
            PASSWORD: ''
        }
    }
    testerrordict = {
        ACTION: 'prsence',
        USER: {
            AUTHUSER: 'guest',
            PASSWORD: ''
        }
    }

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @unittest.skip
    def testKeyError(self):
        '''
        Проверка KeyError (Пропускается-тест должен вернуть fail)
        '''
        self.assertRaises(KeyError, parcing_msg, self.testerrordict)

    @unittest.skip
    def testValueError(self):
        '''
        Проверка ValueError (Пропускается-тест должен вернуть fail)
        '''
        self.assertRaises(ValueError, parcing_msg, self.testerrordict)

    @unittest.skip
    def testTypeErrorr(self):
        '''
        Проверка TypeError(Пропускапется-тест должен вернуть fail)
        '''
        self.assertRaises(TypeError, parcing_msg, self.testlist)

    def test_true_data(self):
        """Проверка корректного presence-сообщеня"""
        self.assertEqual(parcing_msg(self.testdict), ANS_200)

    def test_fail_data(self):
        """Проверка ошибки ключа действия"""
        self.assertEqual(parcing_msg({ACTION: 'prsence', USER: 'guest'}), ANS_400)

    def test_no_key_user(self):
        """Проверка отсутствия ключа 'USER'"""
        self.assertEqual(parcing_msg({ACTION: 'prsence'}), ANS_400)

    def test_no_key_action(self):
        """Проверка отсутствия ключа 'ACTION'"""
        self.assertEqual(parcing_msg({USER: 'guest'}), ANS_400)

    def test_data_no_dict(self):
        """Проверка неверного типа данных аргумента функции"""
        self.assertEqual(parcing_msg(self.testlist), ANS_400)

    def test_date_none(self):
        """Проверка передачи пустого словаря в агрумент"""
        self.assertEqual(parcing_msg({}), ANS_400)


class TestServerparse_adress_in_argv(unittest.TestCase):

    @patch.object(sys, 'argv', ['server.py', '-a', '127.0.0.1'])
    def test_normal(self):
        """ Проверяем вывод функции при нормальном задании адреса"""
        self.assertEqual(parse_adress_in_argv(['server.py', '-a', '127.0.0.1']), '127.0.0.1')

    @patch.object(sys, 'argv', ['server.py'])
    def test_defult_adress(self):
        """ Проверяем вывод функции при отсутствии задании адреса в командной строке"""
        self.assertEqual(parse_adress_in_argv(sys.argv), '')

    @patch.object(sys, 'argv', ['server.py', '-a', '12777777.0.0.1'])
    def test_no_corre_adress(self):
        """ Проверяем вывод функции при ошибочном задании адреса"""
        self.assertEqual(parse_adress_in_argv(sys.argv), '')

    @patch.object(sys, 'argv', ['server.py', '-a:', '127.0.0.1'])
    def test_no_correct_adress(self):
        """ Проверяем вывод функции при ошибочном задании адреса"""
        self.assertEqual(parse_adress_in_argv(sys.argv), '')

    @patch.object(sys, 'argv', ['server.py', '-a', '127.0.0.1'])
    def test_true_patern_addres(self):
        """Проверка корректного ip-адреса в командной строке"""
        self.assertRegex(parse_adress_in_argv(sys.argv), VALID_ADR)

    @patch.object(sys, 'argv', ['server.py', '-a', '1277.0.7770.1'])
    def test_fails_patern_addres(self):
        """Проверка не корректного ip-адреса в командной строке"""
        self.assertNotRegex(parse_adress_in_argv(sys.argv), VALID_ADR)

    @patch.object(sys, 'argv', ['server.py', '127.0.0.1'])
    def test_no_correct_adress1(self):
        """ Проверяем вывод функции при ошибочном задании адреса"""
        self.assertEqual(parse_adress_in_argv(sys.argv), '')


    @unittest.skip
    def test_IndexError(self):
        """ Проверка IndexError (Пропускается-тест должен вернуть fail)"""
        self.assertRaises(IndexError, parse_adress_in_argv, sys.argv)

    @unittest.skip
    def test_TypeError(self):
        """ Проверка TypeError (Пропускается-тест должен вернуть fail)"""
        self.assertRaises(TypeError, parse_adress_in_argv, (1, 2, 3))

    @unittest.skip
    def test_ValueError(self):
        """ Проверка ValueError (Пропускается-тест должен вернуть fail)"""
        self.assertRaises(ValueError, parse_adress_in_argv, ['server.py', '-a'])


class TestServerparse_port_in_argv(unittest.TestCase):

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

    @patch.object(sys, 'argv', ['server.py', '-a', '127.0.0.1', '-p:', 887777])
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
