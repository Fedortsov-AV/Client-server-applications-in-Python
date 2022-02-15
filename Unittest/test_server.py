import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from server import parcing_msg
from common.variables import ANS_200, ANS_400, ACTION, USER


class TestServerpParcing_msg(unittest.TestCase):
    '''
        Тестирование функций сервера
    '''
    testlist = [1, 2, 3]
    testtuple = (1, 2, 3)
    testdict = {ACTION: 'presence', USER: 'guest'}

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @unittest.skip
    def testKeyError(self):
        '''
        Проверка KeyError (Пропускается-тест должен вернуть fail)
        '''
        self.assertRaises(KeyError, parcing_msg, {ACTION: 'presence'})

    @unittest.skip
    def testValueError(self):
        '''
        Проверка ValueError (Пропускается-тест должен вернуть fail)
        '''
        self.assertRaises(ValueError, parcing_msg, {ACTION: 'prsence', USER: 'guest'})

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

    def test_type_ans_200(self):
        """Проверка типа данных в return (ANS_200)"""
        self.assertIsInstance(parcing_msg(self.testdict), dict)

    def test_type_ans_400(self):
        """Проверка типа данных в return (ANS_400)"""
        self.assertIsInstance(parcing_msg(self.testlist), dict)


if __name__ == '__main__':
    unittest.main()
