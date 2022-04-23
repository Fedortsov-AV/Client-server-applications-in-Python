import time
from subprocess import Popen, CREATE_NEW_CONSOLE


def main():
    p_list = []

    count = 3

    while True:
        user = input(f"Запустить {count} клиентов (s) / Закрыть клиентов (x) / Выйти (q) ")

        if user == 'q':
            break
        elif user == 's':
            p_list.append(Popen('python serverUI.py', creationflags=CREATE_NEW_CONSOLE))
            time.sleep(2)
            for _ in range(count):
                p_list.append(Popen('python ClientGUI.py', creationflags=CREATE_NEW_CONSOLE))
            print(f'Запущено {count} клиента и сервер')
        elif user == 'x':
            for p in p_list:
                p.kill()
            p_list.clear()


if __name__ == '__main__':
    main()
