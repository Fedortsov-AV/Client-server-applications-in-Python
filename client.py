import sys
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import send_message, get_message
from common.variables import DEFAULT_PORT, DEFAULT_ADR, VALID_ADR, VALID_PORT, MAX_LEN_MSG

print(sys.argv)
print(VALID_ADR.findall(sys.argv[1]))

def presence_msg():
    msg = {
        'ACTION': 'presence',
        'USER': 'guest'
    }
    return msg

if VALID_ADR.findall(sys.argv[1]):
    ADDRES = VALID_ADR.findall(sys.argv[1])[0]
    print(ADDRES)
else:
    ADDRES = DEFAULT_ADR
    print('Установлен ip-адрес \'%s\', в строке параметров отсутствует задание ip-адреса соответствующее шаблону' % (
        DEFAULT_ADR))

if VALID_PORT.findall(sys.argv[2]):
    PORT = int(VALID_PORT.findall(sys.argv[2])[0])
    print(PORT)
else:
    PORT = int(DEFAULT_PORT)
    print('Установлен ip-адрес \'%s\', в строке параметров отсутствует задание ip-адреса соответствующее шаблону' % (
        DEFAULT_ADR))

print('%s:%d' % (ADDRES, PORT))
SRVSOCK = socket(AF_INET, SOCK_STREAM)
SRVSOCK.connect((ADDRES, PORT))
PRESENCE_MSG = presence_msg()
send_message(PRESENCE_MSG, SRVSOCK)
DATA = get_message(SRVSOCK)
print(DATA)


