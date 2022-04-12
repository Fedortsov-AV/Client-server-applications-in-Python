import sys
from time import sleep

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication
from sqlalchemy import and_

from client import UserClient
from client_db import init_db, UserContact, MessageHistory


class AuthWindow(QWidget):
    # changed_name = pyqtSignal(str)


    def __init__(self):
        super().__init__()
        self.contact_window = ContactWindow()



        self.client = Client()
        self.setWindowTitle('Окно авторизации')

        self.text = QtWidgets.QLabel()
        self.text.setText('Введите ваше имя:')

        self.name = QtWidgets.QLineEdit()



        self.btm = QtWidgets.QPushButton()
        self.btm.setText('Войти')
        self.btm.clicked.connect(self.show_contact)
        # self.btm.clicked.connect(self.on_changed_name)


        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.name)

        self.layout.addWidget(self.btm)
        self.setLayout(self.layout)






    def show_contact(self):
        global session
        session = init_db(self.name.text())
        if not self.client.running:
            self.client.name = self.name.text()
            self.client.initSRV()

        self.contact_window.username = self.name.text()
        self.contact_window.use_client = self.client
        self.contact_window.show_list()
        self.contact_window.show()
        self.hide()







class ContactWindow(QWidget):
    username = None
    use_client = None


    def __init__(self, ):
        super().__init__()
        self.add_show = ContactAdd(self)
        # self.add_show.setWindowModality(QtCore.Qt.WindowModal)


        self.setWindowTitle('Контакты')
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
        print("item = `{}`, itemNumber = `{}`".format(item, itemNumber))



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
            while True:
                if len(contact_name) < 20:
                    contact_name = contact_name + ' '
                    continue
                break
            newitem = f'{contact_name}({message.count()})'
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





class Client(QtCore.QObject):
    running = False
    name = None




    def __init__(self):
        super().__init__()
        self.client = UserClient()
        # Заранее зададим адрес и порт сервера
        self.client.port = 7777
        self.client.addres = '127.0.0.1'

        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)

    def initSRV(self):
        self.running = True
        self.client.session = session
        self.client.user_name = self.name
        self.thread.start()


    def stop(self):
        if self.running:
            self.client.flag_socket = False
            self.running = False
            sleep(1)
            self.thread.terminate()

    # метод, для старта клиента в отдельном потоке
    def run(self):
        if not self.client.flag_socket:
            self.client.run_client()

    def add_contact(self, username: str):
        self.client.add_contact(username)

    def del_contact(self, username: str):
        self.client.del_contact(username)

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

if __name__ == '__main__':
    # client = UserClient()

    app = QApplication(sys.argv)
    main = AuthWindow()


    main.show()
    sys.exit(app.exec_())