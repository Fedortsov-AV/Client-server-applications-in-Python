import time
from subprocess import Popen, CREATE_NEW_CONSOLE

p_list = []

while True:
    user = input("Запустить 4 клиентов (s) / Закрыть клиентов (x) / Выйти (q) ")

    if user == 'q':
        break
    elif user == 's':
        p_list.append(Popen('python server.py',
                            creationflags=CREATE_NEW_CONSOLE))
        time.sleep(1)
        for _ in range(2):
            p_list.append(Popen('python client.py 127.0.0.1 7777 send',
                                creationflags=CREATE_NEW_CONSOLE))

        for _ in range(2):
            p_list.append(Popen('python client.py 127.0.0.1 7777 get',
                                creationflags=CREATE_NEW_CONSOLE))

        print(' Запущено 4 клиента и сервер')
    elif user == 'x':
        for p in p_list:
            p.kill()
        p_list.clear()
