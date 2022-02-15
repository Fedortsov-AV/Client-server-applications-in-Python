import sys
from socket import socket, AF_INET, SOCK_STREAM

from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, VALID_ADR, VALID_PORT, ANS_200, ANS_400, ACTION, USER


def parcing_msg(input_date: dict):
    try:
        if isinstance(input_date, dict):
            if input_date[ACTION] and input_date[USER]:
                if input_date[ACTION] == 'presence':
                    return ANS_200
                raise ValueError
            raise KeyError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (KeyError, TypeError, ValueError):
            return ANS_400


def main():
    if '-a' in sys.argv and VALID_ADR.findall(sys.argv[sys.argv.index('-a') + 1]):
        ADDRES = VALID_ADR.findall(sys.argv[sys.argv.index('-a') + 1])[0]
    else:
        ADDRES = ''
        print(
            'Установлен ip-адрес \'%s\', в строке параметров отсутствует задание ip-адреса соответствующее шаблону' % (
                ADDRES))

    if '-p' in sys.argv and VALID_PORT.findall(sys.argv[sys.argv.index('-p') + 1]):
        PORT = int(VALID_PORT.findall(sys.argv[sys.argv.index('-p') + 1])[0])
        if PORT < 1024 or PORT > 65535:
            PORT = DEFAULT_PORT
            print('Установлен порт %d,  указанный в строке состояния порт не соответствует диапазону 1024 - 65535' % (
                DEFAULT_PORT))
    else:
        PORT = int(DEFAULT_PORT)
        print(
            'Установлен порт %d, в строке параметров отсутствует задание порта соответствующее шаблону' % DEFAULT_PORT)

    print('%s:%d' % (ADDRES, PORT))
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((ADDRES, PORT))
    s.listen(5)

    while True:
        client, addr = s.accept()
        print("Запрос на соединение от ", addr)
        try:
            data = get_message(client)
            print('Сообщение: ', data, ', было отправлено клиентом: ', addr, 'type data=', type(data))
            msg = parcing_msg(data)
            send_message(msg, client)
            client.close()
        except ConnectionResetError:
            client.close()


if __name__ == '__main__':
    main()
