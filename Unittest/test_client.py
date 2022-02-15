import os
import re
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.join(os.getcwd(), '..'))
from client import parsing_msg, parse_addres_in_cmd, parse_port_in_cmd
from common.variables import ANS_200, TIME, RESPONSE, ALERT, VALID_ADR, VALID_PORT


class TestClientParsingMsg(unittest.TestCase):
    """
        Тестирование функции parsing_msg клиента
    """
    testlist = [1, 2, 3]
    testtuple = (1, 2, 3)
    paterfortest = re.compile(r'\d{2}\.\d{2}\.\d{4} \d{2}:\d{2} - \d{3} : \S*')
    testANS_200 = {
        RESPONSE: 200000,

    }

    testANS_400 = {

        ALERT: 'Неправильный запрос/JSON-объект',
        TIME: 1
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
        self.assertRaises(KeyError, parsing_msg, self.testANS_200)

    @unittest.skip
    def testValueError(self):
        """
        Проверка ValueError (Пропускается-тест должен вернуть fail)
        """
        self.assertRaises(ValueError, parsing_msg, self.testANS_400)

    @unittest.skip
    def testTypeErrorr(self):
        """
        Проверка TypeError(Пропускапется-тест должен вернуть fail)
        """
        self.assertRaises(TypeError, parsing_msg, self.testlist)

    def test_true_data(self):
        """Проверка корректного ANS_200-сообщеня"""
        self.assertRegex(parsing_msg(ANS_200), self.paterfortest)

    def test_fail_data(self):
        """Проверка некорректного ANS_200-сообщеня"""
        self.assertNotRegex(parsing_msg(self.testANS_200), self.paterfortest)

    def test_no_key_resrponce(self):
        """Проверка отсутствия ключа 'RESPONCE'"""
        self.assertEqual(parsing_msg(self.testANS_400), 'Неправильный ответ/JSON-объект')

    def test_no_key_alert(self):
        """Проверка отсутствия ключа 'ALERT'"""
        self.assertEqual(parsing_msg(self.testANS_200), 'Неправильный ответ/JSON-объект')

    def test_no_key_time(self):
        """Проверка отсутствия ключа 'TIME'"""
        self.assertEqual(parsing_msg(self.testANS_200), 'Неправильный ответ/JSON-объект')

    def test_data_no_dict(self):
        """Проверка неверного типа данных аргумента функции"""
        self.assertEqual(parsing_msg(self.testlist), 'Неправильный ответ/JSON-объект')

    def test_date_none(self):
        """Проверка передачи пустого словаря в агрумент"""
        self.assertEqual(parsing_msg({}), 'Неправильный ответ/JSON-объект')


class TestClientParseAddres(unittest.TestCase):
    """Тестирование функции parse_addres_in_cmd клиента"""

    @unittest.skip
    def testIndexError(self):
        """
        Проверка IndexError (Пропускается-тест должен вернуть fail)
        """
        self.assertRaises(IndexError, parse_addres_in_cmd, ['server.py'])

    @unittest.skip
    def testTypeErrorr(self):
        """
        Проверка TypeError(Пропускапется-тест должен вернуть fail)
        """
        self.assertRaises(TypeError, parse_addres_in_cmd, ('client.py', '0'))

    @patch.object(sys, 'argv', ['client.py'])
    def test_defult_addres(self):
        """ Проверяем вывод функции при отсутствии задании адреса в командной строке"""
        self.assertEqual(parse_addres_in_cmd(sys.argv), '127.0.0.1')

    @patch.object(sys, 'argv', ['client.py', '127.10.0.1'])
    def test_normal_addres(self):
        """ Проверяем вывод функции при нормальном задании адреса в командной строке"""
        self.assertEqual(parse_addres_in_cmd(sys.argv), '127.10.0.1')

    @patch.object(sys, 'argv', ['client.py', '1270.100.1'])
    def test_fail_addres(self):
        """ Проверяем вывод функции при ошибочном задании адреса в командной строке"""
        self.assertEqual(parse_addres_in_cmd(sys.argv), '127.0.0.1')

    @patch.object(sys, 'argv', ['client.py', '127.0.0.1'])
    def test_true_patern_addres(self):
        """Проверка корректного ip-адреса в командной строке"""
        self.assertRegex(parse_addres_in_cmd(sys.argv), VALID_ADR)

    @unittest.skip
    @patch.object(sys, 'argv', ['client.py', '127.0.0.1'])
    def test_true_patern_addres(self):
        """Проверка корректного ip-адреса в командной строке(Пропускапется-тест должен вернуть fail)"""
        self.assertNotRegex(parse_addres_in_cmd(sys.argv), VALID_ADR)


class TestClientParsePort(unittest.TestCase):
    """Тестирование функции parse_port_in_cmd клиента"""

    @unittest.skip
    def testIndexError(self):
        """
        Проверка IndexError (Пропускается-тест должен вернуть fail)
        """
        self.assertRaises(IndexError, parse_port_in_cmd, ['client.py'])

    @unittest.skip
    def testTypeErrorr(self):
        """
        Проверка TypeError(Пропускапется-тест должен вернуть fail)
        """
        self.assertRaises(TypeError, parse_port_in_cmd, ('client.py', '127.0.0.1', '7777'))

    @unittest.skip
    def testValueError(self):
        """
        Проверка ValueError(Пропускапется-тест должен вернуть fail)
        """
        self.assertRaises(ValueError, parse_port_in_cmd, ['client.py', '127.0.0.1', '77777'])

    @patch.object(sys, 'argv', ['client.py'])
    def test_defult_port(self):
        """ Проверяем вывод функции при отсутствии задании порта в командной строке"""
        self.assertEqual(parse_port_in_cmd(sys.argv), 7777)

    @patch.object(sys, 'argv', ['client.py', '127.10.0.1', '7777'])
    def test_normal_port(self):
        """ Проверяем вывод функции при нормальном задании порта в командной строке"""
        self.assertEqual(parse_port_in_cmd(sys.argv), 7777)

    @patch.object(sys, 'argv', ['client.py', '1270.100.1', '777777'])
    def test_fail_port(self):
        """ Проверяем вывод функции при ошибочном задании порта в командной строке"""
        self.assertEqual(parse_port_in_cmd(sys.argv), 7777)

    @patch.object(sys, 'argv', ['client.py', '127.0.0.1', '7777'])
    def test_true_patern_addres(self):
        """Проверка корректного порта в командной строке"""
        self.assertRegex(parse_port_in_cmd(sys.argv), VALID_PORT)

    @unittest.skip
    @patch.object(sys, 'argv', ['client.py', '127.0.0.1', '77 777'])
    def test_true_patern_addres(self):
        """Проверка корректного порта в командной строке(Пропускапется-тест должен вернуть fail)"""
        self.assertNotRegex(parse_port_in_cmd(sys.argv), VALID_ADR)


if __name__ == '__main__':
    unittest.main()
