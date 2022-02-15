import sys
from socket import socket, AF_INET, SOCK_STREAM

from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, VALID_ADR, VALID_PORT, ANS_200, ANS_400, ACTION, USER, TIME, AUTHUSER


def parcing_msg(input_date: dict):
    try:
        print(input_date[USER])
        if isinstance(input_date, dict):
            if input_date[ACTION] and input_date[USER][AUTHUSER] and input_date[TIME]:
                if input_date[ACTION] == 'presence' and input_date[USER][AUTHUSER] == 'guest':
                    return ANS_200
                raise ValueError
            raise KeyError
        raise TypeError
    finally:
        if sys.exc_info()[0] in (KeyError, TypeError, ValueError):
            return ANS_400

def parse_adress_in_argv(arg: list):
    if '-a' in arg and VALID_ADR.findall(arg[sys.argv.index('-a') + 1]):
        ADDRES = VALID_ADR.findall(arg[arg.index('-a') + 1])[0]
        return ADDRES
    else:
        ADDRES = ''
        print(
            'Установлен ip-адрес \'%s\', в строке параметров отсутствует задание ip-адреса соответствующее шаблону' % (
                ADDRES))
        return ADDRES

def parse_port_in_argv(arg: list):
    if '-p' in arg and VALID_PORT.findall(arg[arg.index('-p') + 1]):
        PORT = int(VALID_PORT.findall(arg[arg.index('-p') + 1])[0])
        if PORT < 1024 or PORT > 65535:
            PORT = DEFAULT_PORT
            print('Установлен порт %d,  указанный в строке состояния порт не соответствует диапазону 1024 - 65535' % (
                DEFAULT_PORT))
            return PORT
        else:
            PORT = int(DEFAULT_PORT)
            print(
                'Установлен порт %d, в строке параметров отсутствует задание порта соответствующее шаблону' % DEFAULT_PORT)
            return PORT
    else:
        PORT = int(DEFAULT_PORT)
        return PORT


def main():
    ADDRES = parse_adress_in_argv(sys.argv)
    PORT = parse_port_in_argv(sys.argv)

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
