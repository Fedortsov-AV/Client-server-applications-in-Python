"""Основной модуль клиента. В нем создается графический интерфейс, а так же
происходит создание экземпляра UserClient и его запуск"""
import logging
import sys
import time

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox
from sqlalchemy import or_
from configparser import ConfigParser


from client import UserClient, parse_port_in_cmd, parse_addres_in_cmd
from client_db import init_db, UserContact, MessageHistory
from common.decorator import verify_edit
from log import client_log_config

logger = logging.getLogger('client')


class AuthWindow(QWidget):
    """ Класс создающий окно авторизации"""

    DB_PATH: str = ''

    def __init__(self):
        super().__init__()
        self.client = UserClient()
        self.contact_window = ContactWindow()
        self.contact_window.use_client = self.client

        self.setWindowTitle('Окно авторизации')
        self.setWindowIcon(QIcon('static/clienticon.png'))

        self.text = QtWidgets.QLabel()
        self.text.setText('Введите ваше имя:')

        self.text1 = QtWidgets.QLabel()
        self.text1.setText('Введите пароль:')

        self.name = QtWidgets.QLineEdit()

        self.visibleIcon = QIcon("static/eye_visible.svg")
        self.hiddenIcon = QIcon("static/eye_hidden.svg")
        self.passworld = QtWidgets.QLineEdit()
        self.passworld.setEchoMode(QtWidgets.QLineEdit.Password)
        self.togglepasswordAction = self.passworld.addAction(self.visibleIcon, QtWidgets.QLineEdit.TrailingPosition)
        self.togglepasswordAction.triggered.connect(self.on_toggle_password_action)
        self.passworld.password_shown = False

        self.auth = QtWidgets.QPushButton()
        self.auth.setShortcut('Enter')
        self.auth.setText('Войти')
        self.auth.clicked.connect(self.authentication)

        self.register = QtWidgets.QPushButton()
        self.register.setText('Зарегистрироваться')
        self.register.clicked.connect(self.registration)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.text1)
        self.layout.addWidget(self.passworld)

        self.layout.addWidget(self.auth)
        self.layout.addWidget(self.register)
        self.setLayout(self.layout)

    def on_toggle_password_action(self):
        """Метод позволяющий отобразить вводимый пароль в окне авторизации"""

        if not self.passworld.password_shown:
            self.passworld.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.passworld.password_shown = True
            self.togglepasswordAction.setIcon(self.hiddenIcon)
        else:
            self.passworld.setEchoMode(QtWidgets.QLineEdit.Password)
            self.passworld.password_shown = False
            self.togglepasswordAction.setIcon(self.visibleIcon)

    @verify_edit
    def start_client(self):
        """Метод запускающий поток UserClient()"""

        if not self.client.running:
            self.client.user_name = self.name.text()
            self.client._password = self.passworld.text()
            self.client.messeg_client.connect(self.message_server)
            self.client.start()

    def authentication(self):
        """Метод проводящий аутендификацию пользователя"""

        self.start_client()
        self.contact_window.setWindowTitle(f'Контакты {self.name.text()}')
        time.sleep(0.5)

        if self.client.running:
            self.client.authentication()
            if not self.client.session:
                self.init_bd_session()

    def registration(self):
        """Метод проводящий регистрацию пользователя"""

        self.start_client()
        self.contact_window.setWindowTitle(f'Контакты {self.name.text()}')
        while not self.client.running:
            time.sleep(0.5)
        print(f'Клиент запущен')
        if self.client.running:
            self.client.registration()
            if not self.client.session:
                self.init_bd_session()

    def init_bd_session(self):
        pass

    def message_server(self, value: str) -> QMessageBox:
        """Метод принимающий сигналы из потока UserClient()"""

        if value in ["Вход выполнен", "Регистрация успешна"]:
            logger.debug(f'Создаю сессию Имя: {self.name.text()} Путь:{self.DB_PATH}')
            global session
            session = init_db(self.name.text(), self.DB_PATH)
            self.client.session = session
            self.contact_window.show_list()
            self.contact_window.show()
            self.hide()
            return QMessageBox.information(self, "Предупреждение", value, QMessageBox.Ok)

        return QMessageBox.critical(self, "Предупреждение", value, QMessageBox.Ok)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.client.exit_msg()


class ContactWindow(QWidget):
    """ Класс создающий окно контактов пользователя"""

    username = None
    use_client = None

    def __init__(self):
        super().__init__()
        self.add_show = ContactAdd(self)
        self.setWindowTitle(f'Контакты {self.username}')
        self.setWindowIcon(QIcon('static/clienticon.png'))
        self.contacts = QtWidgets.QListWidget()
        self.contacts.itemDoubleClicked.connect(self.chat)

        self.addbtn = QtWidgets.QPushButton()
        self.addbtn.setText('Добавить')
        self.addbtn.clicked.connect(self.show_add_window)

        self.delbtn = QtWidgets.QPushButton()
        self.delbtn.setStatusTip('Удалить выбранный контакт')
        self.delbtn.setText('Удалить')
        self.delbtn.clicked.connect(self.del_contact)

        self.gorisontal_layout = QtWidgets.QHBoxLayout()
        self.gorisontal_layout.addWidget(self.addbtn)
        self.gorisontal_layout.addWidget(self.delbtn)

        self.verticallayout = QtWidgets.QVBoxLayout()
        self.verticallayout.addWidget(self.contacts)
        self.verticallayout.addLayout(self.gorisontal_layout)
        self.setLayout(self.verticallayout)
        self.boldfont = QtGui.QFont()
        self.defaultfont = QtGui.QFont()
        self.boldfont.setBold(True)
        self.defaultfont.setBold(False)

    def chat(self):
        itemNumber = self.contacts.currentRow()
        item = self.contacts.item(itemNumber).text()
        ChatWindow(self, contact_name=item[:19].strip())

    def contact_list(self):
        """Метод получает список контактов и новых сообщений из БД.
         Обновляет информацию о них в окне контактов пользователя.
        """

        if session:
            contact = session.query(UserContact)
            while True:
                if contact.count() < self.contacts.count():
                    self.contacts.clear()
                    continue
                elif contact.count() > self.contacts.count():
                    self.contacts.addItem(QtWidgets.QListWidgetItem(''))
                    continue
                break
            for _ in range(contact.count()):
                contact_name = str(contact[_].contact)
                message = session.query(MessageHistory).filter_by(msg_to=contact[_].contact, readed=0)

                newitem = f'{contact_name.ljust(20, " ")}({message.count()})'
                if newitem != self.contacts.item(_).text():
                    self.contacts.item(_).setText(newitem)
                    if message.count() != 0:
                        self.contacts.item(_).setFont(self.boldfont)
                    else:
                        self.contacts.item(_).setFont(self.defaultfont)

    def show_list(self):
        """Метод создает и запускает таймер для отслеживания состояния контактов (списка контактов и новых сообщений)"""

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.contact_list)
        self.timer.start()

    def del_contact(self):
        """Метод запускающий функционал удаления контакта"""

        itemNumber = self.contacts.currentRow()
        item = self.contacts.item(itemNumber).text()
        self.use_client.del_contact(item[:19].strip())

    def add_contact(self, name: str):
        """Метод запускающий функционал добавления контакта"""

        self.use_client.add_contact(name)
        self.add_show.hide()

    def show_add_window(self):
        """Метод открывает диалог добавления контакта"""

        self.add_show.show()

    def info(self, value: str):
        """Метод принимающий сигналы из потока UserClient()"""

        return QMessageBox.information(self, "Предупреждение", value, QMessageBox.Ok)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.use_client.exit_msg()


class ContactAdd(QtWidgets.QDialog):
    """ Класс создающий диалог добавления контакта"""

    def __init__(self, root):
        super().__init__(root)
        self.contact = root
        self.setWindowTitle('Добавить контакт')
        self.setWindowIcon(QIcon('static/clienticon.png'))
        self.line_edit = QtWidgets.QLineEdit()

        self.btn = QtWidgets.QPushButton()
        self.btn.setText('OK')
        self.btn.clicked.connect(self.add)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.btn)
        self.setLayout(self.layout)

    def add(self):
        """Метод запускающий функционал добавления контакта"""

        username = self.line_edit.text()
        self.contact.add_contact(username)


class ChatWindow(QtWidgets.QDialog):
    """ Класс создающий окно чата с контактом"""

    def __init__(self, root: QtWidgets.QWidget, contact_name=None):
        super().__init__(root)
        self.contact = contact_name
        self.main = root
        self.setWindowTitle(f'Чат с {contact_name}')
        self.setWindowIcon(QIcon('static/clienticon.png'))

        self.chat = QtWidgets.QListWidget()
        self.chat.setWordWrap(True)
        self.chat.setTextElideMode(QtCore.Qt.ElideNone)
        self.chat_history()

        self.message = QtWidgets.QLineEdit()

        self.send = QtWidgets.QPushButton()
        self.send.setText('send')
        self.send.setIcon(QIcon('static/play.png'))
        self.send.clicked.connect(self.send_msg)

        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.chat, 0, 0, 5, 7)
        self.grid.addWidget(self.message, 5, 0, 1, 6)
        self.grid.addWidget(self.send, 5, 6)

        self.setLayout(self.grid)

        self.refresh = QTimer()
        self.refresh.setInterval(1000)
        self.refresh.timeout.connect(self.refresh_chat)
        self.refresh.start()
        self.show()

    def chat_history(self):
        """Метод отображает историю переписки с пользователем в окне чата"""

        messagebox = session.query(MessageHistory).filter(
            or_(MessageHistory.msg_to == self.contact, MessageHistory.msg_from == self.contact))

        for _ in messagebox.all():
            _.readed = 1
        session.commit()

        messagebox.order_by(MessageHistory.create_time)

        for _ in range(messagebox.count()):
            message = f'{messagebox[_].create_time.strftime("%H:%M:%S")}\n {messagebox[_].text_message}'
            item = QtWidgets.QListWidgetItem(message)
            if messagebox[_].msg_to == self.contact:
                item.setTextAlignment(1)
                self.chat.addItem(item)
            else:
                item.setTextAlignment(2)
                self.chat.addItem(item)
            self.chat.scrollToItem(item)

    def refresh_chat(self):
        """Метод обновляет историю переписку в окне чата"""

        if self.isVisible():
            messagebox = session.query(MessageHistory).filter_by(readed=0)
            if messagebox.count() > 0:
                for _ in messagebox:
                    if self.contact in (_.msg_to, _.msg_from):
                        message = f'{_.create_time.strftime("%H:%M:%S")}\n {_.text_message}'
                        item = QtWidgets.QListWidgetItem(message)
                        if _.msg_to == self.contact:
                            item.setTextAlignment(1)
                            self.chat.addItem(item)
                        else:
                            item.setTextAlignment(2)
                            self.chat.addItem(item)
                        _.readed = 1
                        self.chat.scrollToItem(item)
            session.commit()

    def send_msg(self):
        """Метод запускает функционал отправки сообщения пользователю"""

        if self.message.text().strip() != '':
            self.main.use_client.send_msg(self.message.text(), self.contact)
            self.message.clear()


def main():
    config = ConfigParser()
    config.read('client_config.ini')

    app = QApplication(sys.argv)
    main = AuthWindow()
    main.DB_PATH = config['DataBase']['PATH']
    main.client.DB_PATH = config['DataBase']['PATH']

    PORT = parse_port_in_cmd(sys.argv)
    ADDRES = parse_addres_in_cmd(sys.argv)
    main.client.port = config['Client']['PORT']
    main.client.addres = config['Client']['ADDRES']


    if PORT and PORT != config['Client']['PORT']:
        main.client.port = PORT

    if ADDRES and ADDRES != config['Client']['ADDRES']:
        main.client.addres = ADDRES

    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


