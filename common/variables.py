import datetime
import re
import time

DEFAULT_PORT = 7777
DEFAULT_ADR = '127.0.0.1'
MAX_LEN_MSG = 1024
VALID_ADR = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
VALID_PORT = re.compile(r'^\d{4,5}$')
ENCODE = 'utf-8'

ACTION = 'ACTION'
USER = 'USER'
RESPONCE = 'RESPONCE'
ALERT = 'ALERT'
TIME = 'TIME'
AUTHUSER = 'USER'
PASSWORD = 'PASSWORD'


ANS_200 = {
    RESPONCE: 200,
    ALERT: 'ОК',
    TIME: time.time()
}

ANS_400 = {
    RESPONCE: 400,
    ALERT: 'Неправильный запрос/JSON-объект',
    TIME: time.time()
}
