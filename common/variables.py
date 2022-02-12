import re
DEFAULT_PORT = 7777
DEFAULT_ADR = '127.0.0.1'
MAX_LEN_MSG = 1024
VALID_ADR = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
VALID_PORT = re.compile(r'^\d{4,5}$')