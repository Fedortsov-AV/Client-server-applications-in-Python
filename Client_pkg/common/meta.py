"""Модуль содержащий метаклассы"""

import dis



class ServerVerifier(type):
    """Метокласс сервера, проверяет отсутствие вызова метода connect,
    а так же использование TCP (по наличию константы SOCK_STREAM при создании сокета)"""

    def __new__(cls, clsname, bases, clsdict):
        # print(clsdict)
        code = dis.code_info(clsdict['run_socket'])

        if code.find('connect') >= 0:
            raise Exception('Сервер не может вызывать метод  connect для сокетов')

        if code.find('SOCK_STREAM') < 0:
            raise Exception('Использованный тип сокета не предназначен для работы по TCP.')
        return type.__new__(cls, clsname, bases, clsdict)


class ClientVerifier(type):
    """Метокласс клиента, проверяет отсутствие вызова метода accept,
        а так же использование TCP (по наличию константы SOCK_STREAM при создании сокета)"""

    def __new__(cls, clsname, bases, clsdict):
        code = dis.code_info(clsdict['init_socket'])
        if code.find('accept') >= 0 or code.find('listen') >= 0:
            raise Exception('Клиент не может вызывать методы listen или accept для сокетов')
        if code.find('SOCK_STREAM') < 0:
            raise Exception('Использованный сокет не предназначен для работы по TCP.')
        return type.__new__(cls, clsname, bases, clsdict)


if __name__ == '__main__':
    pass
