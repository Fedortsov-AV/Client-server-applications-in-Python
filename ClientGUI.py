import sys
import time

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox
from sqlalchemy import or_

from client import UserClient
from client_db import init_db, UserContact, MessageHistory
from decorator import verify_edit


class AuthWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.client = UserClient()
        self.contact_window = ContactWindow()
        self.contact_window.use_client = self.client

        self.setWindowTitle('Окно авторизации')

        self.text = QtWidgets.QLabel()
        self.text.setText('Введите ваше имя:')

        self.text1 = QtWidgets.QLabel()
        self.text1.setText('Введите пароль:')

        self.name = QtWidgets.QLineEdit()
        #
        self.visibleIcon = QIcon("eye_visible.svg")
        self.hiddenIcon = QIcon("eye_hidden.svg")
        self.passworld = QtWidgets.QLineEdit()
        self.passworld.setEchoMode(QtWidgets.QLineEdit.Password)
        self.togglepasswordAction = self.passworld.addAction(self.visibleIcon, QtWidgets.QLineEdit.TrailingPosition )
        self.togglepasswordAction.triggered.connect(self.on_toggle_password_Action)
        self.passworld.password_shown = False

        self.auth = QtWidgets.QPushButton()
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

    def on_toggle_password_Action(self):
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
        if not self.client.running:
            self.client.user_name = self.name.text()
            self.client._password = self.passworld.text()
            self.client.port = 7777
            self.client.addres = '127.0.0.1'
            self.client.messeg_client.connect(self.message_server)
            self.client.start()


    def authentication(self):
        self.start_client()

        # while not self.client.running:
        #     time.sleep(0.5)
        # print(f'Клиент запущен')
        # while self.client.get == None:
        #     time.sleep(0.5)
        # print(self.client.get)
        self.contact_window.setWindowTitle(f'Контакты {self.name.text()}')
        time.sleep(1)

        if self.client.running:
            self.client.authentication()

    def registration(self):
        self.start_client()
        while not self.client.running:
            time.sleep(0.5)
        print(f'Клиент запущен')
        if self.client.running:
            self.client.registration()

    def message_server(self, value: str) -> QMessageBox:
        if value in ["Вход выполнен", "Регистрация успешна"]:
            global session
            session = init_db(self.name.text())
            self.client.session = session

            self.contact_window.show_list()
            self.contact_window.show()
            self.hide()
            return QMessageBox.information(self, "Предупреждение", value, QMessageBox.Ok)

        return QMessageBox.critical(self, "Предупреждение", value, QMessageBox.Ok)


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.client.exit_msg()


class ContactWindow(QWidget):
    username = None
    use_client = None

    def __init__(self):
        super().__init__()
        self.add_show = ContactAdd(self)
        # self.add_show.setWindowModality(QtCore.Qt.WindowModal)

        self.setWindowTitle(f'Контакты {self.username}')
        # self.setGeometry(100, 100, 600, 250)

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
        self.item_chat = ChatWindow(self, contact_name=item[:19].strip())

    def contact_list(self):
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
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.contact_list)
        self.timer.start()

    def del_contact(self):
        itemNumber = self.contacts.currentRow()
        item = self.contacts.item(itemNumber).text()
        self.use_client.del_contact(item[:19].strip())

    def add_contact(self, name: str):
        self.use_client.add_contact(name)
        self.add_show.hide()

    def show_add_window(self):
        self.add_show.show()

    def info(self, value):
        return QMessageBox.information(self, "Предупреждение", value, QMessageBox.Ok)


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print("Написать серверу, что пользователь отключается!")
        print("Закрываюсь.....")
        self.use_client.exit_msg()

# class Info(QtWidgets.QDialog):
#
#     def __init__(self):
#         super().__init__()
#         self.resize(311, 151)
#         self.groupBox = QtWidgets.QGroupBox(self)
#         self.groupBox.setGeometry(QtCore.QRect(0, 0, 311, 151))
#         self.groupBox.setTitle("")
#         self.lable1 = QtWidgets.QLabel(self.groupBox)
#         self.lable1.setGeometry(QtCore.QRect(20, 40, 71, 61))
#         self.pix = QPixmap('info.jpg')
#         self.lable1.setPixmap(self.pix.scaled(self.lable1.width(), self.lable1.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
#
#
#         self.label = QtWidgets.QLabel(self.groupBox)
#         self.label.setGeometry(QtCore.QRect(110, 40, 171, 61))
#         self.label.setWordWrap(True)
#
#         self.pushButton = QtWidgets.QPushButton(self.groupBox)
#         self.pushButton.setGeometry(QtCore.QRect(110, 120, 75, 23))
#         self.pushButton.setText('OK')
#         self.pushButton.clicked.connect(self.close)
#
#     def show_info(self, text):
#         self.label.setText(str(text))
#         self.show()


class ContactAdd(QtWidgets.QDialog):
    def __init__(self, main):
        super().__init__(main)
        self.contact = main
        self.setWindowTitle('Добавить контакт')
        self.line_edit = QtWidgets.QLineEdit()

        self.btn = QtWidgets.QPushButton()
        self.btn.setText('OK')
        self.btn.clicked.connect(self.add)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.btn)
        self.setLayout(self.layout)

    def add(self):
        username = self.line_edit.text()
        self.contact.add_contact(username)


class ChatWindow(QtWidgets.QDialog):
    def __init__(self, main, contact_name=None):
        super().__init__(main)
        self.contact = contact_name
        self.main = main
        self.setWindowTitle(f'Чат с {contact_name}')

        self.chat = QtWidgets.QListWidget()
        self.chat_history()

        self.message = QtWidgets.QPlainTextEdit()

        self.send = QtWidgets.QPushButton()
        self.send.setText('send')
        self.send.setIcon(QIcon('play.png'))
        self.send.clicked.connect(self.send_msg)

        self.mainlaout = QtWidgets.QVBoxLayout()
        self.hlaout = QtWidgets.QHBoxLayout()

        self.hlaout.addWidget(self.message)
        self.hlaout.addWidget(self.send)

        self.mainlaout.addWidget(self.chat)
        self.mainlaout.addLayout(self.hlaout)

        self.setLayout(self.mainlaout)

        self.refresh = QTimer()
        self.refresh.setInterval(1000)
        self.refresh.timeout.connect(self.refresh_chat)
        self.refresh.start()
        self.show()


    def chat_history(self):
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



    def refresh_chat(self):
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
            session.commit()

    def send_msg(self):
        if self.message.toPlainText().strip() != '':
            self.main.use_client.send_msg(self.message.toPlainText(), self.contact)
            self.message.clear()


if __name__ == '__main__':
    # client = UserClient()

    app = QApplication(sys.argv)
    main = AuthWindow()
    main.show()
    # chat = ChatWindow(main)
    # chat.show()
    sys.exit(app.exec_())
