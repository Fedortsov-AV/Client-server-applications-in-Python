import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from client import presence_msg, parcing_msg
from common.variables import RESPONCE, ALERT, ANS_200

parcing_msg(ANS_200)

# class TestClient(unittest.TestCase):
#     def test_isinstance_parcing_msg(self):
#         self.assertIsInstance(parcing_msg({
#         'RESPONCE': 200,
#         'ALERT': 'ОК'
#     }), dict)