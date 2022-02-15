import os
import re
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from client import parcing_msg
from common.variables import ANS_200, ANS_400, TIME, RESPONCE, ALERT


class TestClientParcing_msg(unittest.TestCase):
    '''
        Тестирование функций сервера
    '''
    testlist = [1, 2, 3]
    testtuple = (1, 2, 3)
    paterfortest = re.compile(r'\d{2}\.\d{2}\.\d{4} \d{2}:\d{2} - \d{3} : \S*')
    testANS_200 = {
        RESPONCE: 200000,

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
        '''
        Проверка KeyError (Пропускается-тест должен вернуть fail)
        '''
        self.assertRaises(KeyError, parcing_msg, self.testANS_200)

    @unittest.skip
    def testValueError(self):
        '''
        Проверка ValueError (Пропускается-тест должен вернуть fail)
        '''
        self.assertRaises(ValueError, parcing_msg, self.testANS_400)

    @unittest.skip
    def testTypeErrorr(self):
        '''
        Проверка TypeError(Пропускапется-тест должен вернуть fail)
        '''
        self.assertRaises(TypeError, parcing_msg, self.testlist)

    def test_true_data(self):
        """Проверка корректного ANS_200-сообщеня"""
        self.assertRegex(parcing_msg(ANS_200), self.paterfortest)

    def test_fail_data(self):
        """Проверка некорректного ANS_200-сообщеня"""
        self.assertNotRegex(parcing_msg(self.testANS_200), self.paterfortest)

    def test_no_key_resrponce(self):
        """Проверка отсутствия ключа 'RESPONCE'"""
        self.assertEqual(parcing_msg(self.testANS_400), 'Неправильный ответ/JSON-объект')

    def test_no_key_alert(self):
        """Проверка отсутствия ключа 'ALERT'"""
        self.assertEqual(parcing_msg(self.testANS_200), 'Неправильный ответ/JSON-объект')

    def test_no_key_time(self):
        """Проверка отсутствия ключа 'TIME'"""
        self.assertEqual(parcing_msg(self.testANS_200), 'Неправильный ответ/JSON-объект')

    def test_data_no_dict(self):
        """Проверка неверного типа данных аргумента функции"""
        self.assertEqual(parcing_msg(self.testlist), 'Неправильный ответ/JSON-объект')

    def test_date_none(self):
        """Проверка передачи пустого словаря в агрумент"""
        self.assertEqual(parcing_msg({}), 'Неправильный ответ/JSON-объект')


if __name__ == '__main__':
    unittest.main()
