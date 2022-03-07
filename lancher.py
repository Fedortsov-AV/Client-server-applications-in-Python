import time
from subprocess import Popen, CREATE_NEW_CONSOLE

p_list = []

count = 3

while True:
    user = input(f"Запустить {count} клиентов (s) / Закрыть клиентов (x) / Выйти (q) ")

    if user == 'q':
        break
    elif user == 's':
        p_list.append(Popen('python server.py',
                            creationflags=CREATE_NEW_CONSOLE))
        time.sleep(1)
        for _ in range(count):
            p_list.append(Popen('python client.py 127.0.0.1 7777',
                                creationflags=CREATE_NEW_CONSOLE))



        print(f'Запущено {count} клиента и сервер')
    elif user == 'x':
        for p in p_list:
            p.kill()
        p_list.clear()
