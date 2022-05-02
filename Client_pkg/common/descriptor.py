"""Модуль содержит дескрипторы"""


class SocketPort:
    """Дескриптор для проверки номера порта"""

    def __set__(self, instance, value):
        if value < 0:
            print("Не может быть отрицательным! Установлен порт по умолчанию")
            instance.__dict__[self.my_attr] = 7777
        if not isinstance(value, int):
            print("Mожет быть только целым числом! Установлен порт по умолчанию")
            instance.__dict__[self.my_attr] = 7777
        instance.__dict__[self.my_attr] = value

    def __set_name__(self, owner, my_attr):

        self.my_attr = my_attr


if __name__ == '__main__':
    pass
