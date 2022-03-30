import dis


# class ClassVerifier(type):
#
#     def __new__(cls, clsname, bases, clsdict):
#         code = dis.code_info(clsdict['run_{}'.format(clsname.lower())])
#
#         if clsdict['__qualname__'] == 'Server':
#             if code.find('connect') >= 0:
#                 raise Exception('Сервер не может вызывать метод  connect для сокетов')
#         if clsdict['__qualname__'] == 'Client':
#             if code.find('accept') >= 0 or code.find('listen') >= 0:
#                 raise Exception('Клиент не может вызывать методы listen или accept для сокетов')
#         if code.find('SOCK_STREAM') < 0:
#             raise Exception('Использованный тип сокета не предназначен для работы по TCP.')
#         return type.__new__(cls, clsname, bases, clsdict)


class ServerVerifier(type):

    def __new__(cls, clsname, bases, clsdict):

        code = dis.code_info(clsdict['run_server'])

        if code.find('connect') >= 0:
            raise Exception('Сервер не может вызывать метод  connect для сокетов')

        if code.find('SOCK_STREAM') < 0:
            raise Exception('Использованный тип сокета не предназначен для работы по TCP.')
        return type.__new__(cls, clsname, bases, clsdict)


class ClientVerifier(type):

    def __new__(cls, clsname, bases, clsdict):
        code = dis.code_info(clsdict['run_client'])
        if code.find('accept') >= 0 or code.find('listen') >= 0:
            raise Exception('Клиент не может вызывать методы listen или accept для сокетов')
        if code.find('SOCK_STREAM') < 0:
            raise Exception('Использованный сокет не предназначен для работы по TCP.')
        return type.__new__(cls, clsname, bases, clsdict)


if __name__ == '__main__':
    pass
