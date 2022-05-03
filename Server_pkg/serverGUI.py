"""Модуль создает графическую оболочку для сервера"""
import os
import sys
from datetime import datetime
from time import sleep

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QTableWidget, QTableWidgetItem, QComboBox, QLabel, \
    QWidget


from server import Server, parse_port_in_argv, parse_addres_in_argv
from server_db import User, UserHistory, init_db
from configparser import ConfigParser


class MainWindow(QMainWindow):
    """Класс создающий основное окно"""

    path_bd: str = ''
    file_name_bd: str = ''

    def __init__(self, session):
        super().__init__()
        self.setWindowTitle('Управление сервером')
        self.setWindowIcon(QIcon('static/Servericon.png'))
        self.session = session
        self.server = Server()

        self.server.finish.connect(self.finish)

        # Формируем окна Активные пользователи и История пользователей
        self.window1 = ListUsers()
        self.window1.setWindowTitle('Активные пользователи')
        name = self.session.query(User)
        activ_name = name.filter_by(online=1)
        for item in activ_name.all():
            item.online = 0
        self.session.commit()
        for item in name.all():
            self.window1.comboBox.addItem(str(item.username))
        self.window1.tableWidget.setColumnCount(4)
        self.window1.tableWidget.setHorizontalHeaderLabels(['ID', 'Имя пользователя', 'IP адрес', 'Время в сети'])
        self.window1.tableWidget.setColumnWidth(0, 50)
        self.window1.tableWidget.setColumnWidth(1, 150)
        self.window1.tableWidget.setColumnWidth(2, 150)
        self.window1.tableWidget.setColumnWidth(3, 200)

        self.window2 = ListUsers()
        self.window2.setWindowTitle('История пользователей')
        for item in name.all():
            self.window2.comboBox.addItem(str(item.username))
        self.window2.tableWidget.setColumnCount(3)
        self.window2.tableWidget.setHorizontalHeaderLabels(['Имя пользователя', 'IP адрес', 'Время подключения'])
        self.window2.tableWidget.setColumnWidth(0, 50)
        self.window2.tableWidget.setColumnWidth(1, 150)
        self.window2.tableWidget.setColumnWidth(2, 200)

        self.window3 = SettingServer(self)
        self.window3.setWindowModality(QtCore.Qt.WindowModal)


        # Формируем таймер для обновления главного списка
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.maintable)

        # Формируем виджет таблицы
        self.table_widget = QTableWidget(0, 4)
        header_labels = ['ID', 'Username', 'IP', 'Last enter']
        self.table_widget.setHorizontalHeaderLabels(header_labels)
        self.setCentralWidget(self.table_widget)

        # Формируем обрабатываемые действия
        exitAction = QAction(QIcon('static/exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        activ_user = QAction('Подключенные пользователи', self)
        activ_user.setShortcut('Ctrl+W')
        activ_user.setStatusTip('Список пользователей подключенных к серверу')
        activ_user.triggered.connect(self.win1)

        user_history = QAction('История подключений пользователей', self)
        user_history.setShortcut('Ctrl+E')
        user_history.setStatusTip('История подключений пользователей к серверу')
        user_history.triggered.connect(self.win2)

        setting_server = QAction('Настройка сервера', self)
        setting_server.setShortcut('Ctrl+R')
        setting_server.setStatusTip('Настройка сервера')
        setting_server.triggered.connect(self.win3)

        start_server = QAction(QIcon('static/play.png'), 'Запустить сервер', self)
        start_server.setShortcut('Ctrl+P')
        start_server.setStatusTip('Запуск сервера')
        start_server.triggered.connect(self.run_serv)

        stop_server = QAction(QIcon('static/stop.png'), 'Остановить сервер', self)
        stop_server.setShortcut('Ctrl+S')
        stop_server.setStatusTip('Остановить сервер')
        stop_server.triggered.connect(self.stop_server)

        # Формируем статусбар, тоолбар и меню
        self.status = self.statusBar()
        self.statuslable1 = QtWidgets.QLabel()
        self.statuslable2 = QtWidgets.QLabel()
        self.statuslable3 = QtWidgets.QLabel()
        # self.statuslaout = QtWidgets.QHBoxLayout()
        self.status.addPermanentWidget(self.statuslable1)
        self.status.addPermanentWidget(self.statuslable2)
        self.status.addPermanentWidget(self.statuslable3)
        # self.status.setLayout(self.statuslaout)
        menubar = self.menuBar()
        self.toolbar = self.addToolBar('Запуск сервера')
        self.toolbar.addAction(start_server)
        self.toolbar.addAction(stop_server)
        self.toolbar.addAction(exitAction)

        # Меню файл (Выход)
        fileMenu = menubar.addMenu('Файл')
        fileMenu.addAction(exitAction)

        # Меню обзор (Подключенные пользователи, История подключений)
        search = menubar.addMenu('Обзор')
        search.addAction(activ_user)
        search.addAction(user_history)

        # Меню обзор (Подключенные пользователи, История подключений)
        serv_action = menubar.addMenu('Действия')
        serv_action.addAction(setting_server)

        self.timer.start()
        self.setGeometry(100, 100, 600, 250)
        self.setWindowTitle('Main window')
        self.statuslable3.setText('Сервер остановлен')

    def win2(self):
        """Метод отображает окно с историей подключений пользователей"""

        if self.window2.isVisible():
            self.window2.hide()
        else:
            self.window2.show()

    def win1(self):
        """Метод отображает окно с активными пользователями"""

        if self.window1.isVisible():
            self.window1.hide()
        else:
            self.window1.show()

    def win3(self):
        """Метод отображающий окно настроек сервера"""

        if self.window3.isVisible():
            self.window3.hide()
        else:
            self.window3.show()
            self.window3.server = self.server

    def maintable(self):
        """Метод обновляет данные в основной таблице, а так же в таблицах активные пользователи
           и история пользователей если они отображаются на экране"""

        activ_users = self.session.query(User)
        # print(f'{activ_users.count()} != {self.table_widget.rowCount()}')
        if activ_users.count() != self.table_widget.rowCount():
            self.table_widget.clearContents()
            self.table_widget.setRowCount(activ_users.count())
            for row in range(0, activ_users.count()):
                history = self.session.query(UserHistory).filter_by(user_id=activ_users[row].id).order_by(
                    UserHistory.login_time.desc())

                self.table_widget.setItem(row, 0, QTableWidgetItem(str(activ_users[row].id)))
                self.table_widget.setItem(row, 1, QTableWidgetItem(activ_users[row].username))
                if history.count() > 0:
                    self.table_widget.setItem(row, 2, QTableWidgetItem(history[0].ip_addres))
                    self.table_widget.setItem(row, 3, QTableWidgetItem(str(history[0].login_time)))
                    # print(f'{activ_users[row].online} - {activ_users[row].username}')
                    # if activ_users[row].online == 1:
                    #     delta = datetime.now() - history[0].login_time
                    #     self.table_widget.setItem(row, 4, QTableWidgetItem(str(delta)))

        # Если открыто окно История подключений, обновляем его содержимое
        if self.window2.isVisible():
            name = self.window2.comboBox.currentText()
            if name == 'Все пользователи':
                history = self.session.query(UserHistory).order_by(UserHistory.login_time.desc())
            else:
                history = self.session.query(UserHistory).filter_by(username=name).order_by(
                    UserHistory.login_time.desc())
            if self.window2.tableWidget.rowCount() != history.count():
                self.window2.tableWidget.clearContents()
                self.window2.tableWidget.setRowCount(history.count())
                for item in range(0, history.count()):
                    self.window2.tableWidget.setItem(item, 0, QTableWidgetItem(str(history[item].username)))
                    self.window2.tableWidget.setItem(item, 1, QTableWidgetItem(str(history[item].ip_addres)))
                    self.window2.tableWidget.setItem(item, 2, QTableWidgetItem(str(history[item].login_time)))

        # Если открыто окно Активные пользователи, обновляем его содержимое
        if self.window1.isVisible():
            self.window1.tableWidget.clearContents()
            activ_users = self.session.query(User).filter_by(online=1)

            self.window1.tableWidget.clearContents()
            self.window1.tableWidget.setRowCount(activ_users.count())
            for row in range(0, activ_users.count()):
                history = self.session.query(UserHistory).filter_by(user_id=activ_users[row].id).order_by(
                    UserHistory.login_time.desc())
                self.window1.tableWidget.setItem(row, 0, QTableWidgetItem(str(activ_users[row].id)))
                self.window1.tableWidget.setItem(row, 1, QTableWidgetItem(activ_users[row].username))

                if history.count() > 0:
                    self.window1.tableWidget.setItem(row, 2, QTableWidgetItem(history[0].ip_addres))
                    if activ_users[row].online == 1:
                        delta = datetime.now() - history[0].login_time
                        self.window1.tableWidget.setItem(row, 3, QTableWidgetItem(str(delta)))



    def run_serv(self):
        """Метод запускающий сервер"""

        self.statuslable3.setText('Сервер запущен')
        self.server.session = self.session
        if not self.server.running:
            self.server.ADDRES = self.window3.lineEdit_3.text()
            self.server.PORT = int(self.window3.lineEdit_4.text())
            self.server.start()

    def stop_server(self):
        """Метод останавливающий сервер"""

        if self.server.running:
            self.server.running = False
            sleep(0.5)
            self.statuslable3.setText('Сервер остановлен')

    def finish(self, value):
        """Метод обрабатывает сигналы от сервера и добавляет их в статус бар"""

        self.statuslable2.setText(value)

    def new_session(self):
        """Метод создает сессию в БД сервера"""

        self.session = init_db(self.path_bd, self.file_name_bd)


class ListUsers(QWidget):
    """Клас создает каркас окна для списка активных пользователей и истории подключений"""

    def __init__(self):
        super().__init__()
        # Формируем основное окно
        self.setWindowIcon(QIcon('static/Servericon.png'))
        self.setGeometry(100, 100, 600, 300)

        # Формируем каркас таблицы
        self.tableWidget = QTableWidget()
        self.tableWidget.setGeometry(QtCore.QRect(0, 40, 361, 461))
        self.tableWidget.setRowCount(0)

        # Формируем каркас списка пользователей
        self.comboBox = QComboBox()
        self.comboBox.setGeometry(QtCore.QRect(180, 10, 121, 22))
        self.comboBox.addItem('Все пользователи')

        # Формируем текстовое поле
        self.label = QLabel()
        self.label.setGeometry(QtCore.QRect(20, 10, 151, 16))
        self.label.setText("Выберите имя пользователя:")

        # Выставляем все на окно используя выравнивания
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.addWidget(self.label)
        self.horizontalLayout.addWidget(self.comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.tableWidget)
        self.setLayout(self.verticalLayout)


class SettingServer(QtWidgets.QDialog):
    """Класс создает окно настроек сервера"""

    def __init__(self, main_window, **kwargs):
        super().__init__(main_window, **kwargs)
        self.main = main_window
        self.setWindowIcon(QIcon('static/Servericon.png'))
        self.setGeometry(QtCore.QRect(100, 100, 400, 139))
        self.setWindowTitle('Настройки сервера')

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setText('DateBase/')
        self.lineEdit_2 = QtWidgets.QLineEdit()
        self.lineEdit_2.setText('serv_db.db3')
        self.lineEdit_3 = QtWidgets.QLineEdit()
        self.lineEdit_3.setText('')
        self.lineEdit_4 = QtWidgets.QLineEdit()
        self.lineEdit_4.setText('7777')

        self.toolButton = QtWidgets.QToolButton()
        self.toolButton.setText("Обзор")
        self.toolButton.clicked.connect(self.brows)

        self.label = QtWidgets.QLabel()
        self.label.setText("Имя файла> БД")
        self.label_2 = QtWidgets.QLabel()
        self.label_2.setText("Адрес сервера: ")
        self.label_3 = QtWidgets.QLabel()
        self.label_3.setText("Порт сервера: ")

        self.pushButton = QtWidgets.QPushButton()
        self.pushButton.setText("Использовать файл БД")
        self.pushButton.setToolTip('Использовать файл БД')
        self.pushButton.clicked.connect(self.use_bd)

        self.pushButton2 = QtWidgets.QPushButton()
        self.pushButton2.setText("Запустить сервер")
        self.pushButton2.setShortcut('Ctrl+R')
        self.pushButton2.setToolTip('Запустить сервер')
        self.pushButton2.clicked.connect(self.run_server)

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()

        self.horizontalLayout.addWidget(self.lineEdit)
        self.horizontalLayout.addWidget(self.toolButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2.addWidget(self.label)
        self.horizontalLayout_2.addWidget(self.lineEdit_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.pushButton)

        self.horizontalLayout_3.addWidget(self.label_2)
        self.horizontalLayout_3.addWidget(self.lineEdit_3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4.addWidget(self.label_3)
        self.horizontalLayout_4.addWidget(self.lineEdit_4)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.verticalLayout.addWidget(self.pushButton2)

        self.setLayout(self.verticalLayout)

    def use_bd(self):
        """Метод создает новую сессию БД"""

        self.main.path_bd = self.lineEdit.text()
        self.main.file_name_bd = self.lineEdit_2.text()
        self.main.new_session()

    def brows(self):
        """Метод создает структуру дерева для кнопки 'обзор'"""

        path = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.lineEdit_2.setText(path.split('/')[-1])
        split_list = path.split('/')
        text = ''
        for _ in range(0, len(split_list) - 1):
            text = text + split_list[_] + '/'

        self.lineEdit.setText(text)

    def run_server(self):
        """Метод запускающий сервер"""

        if not self.main.server.running:
            self.main.server.address = self.lineEdit_3.text()
            self.main.server.port = int(self.lineEdit_4.text())
            self.main.run_serv()


def main():
    """Основной цикл сервера.
    Получает данные из файла server_config.ini, а так же проверяет
    параметры командной строки. Если в командной строке установлен адрес или порт
    отвечающие критериям, то использует их!"""

    config = ConfigParser()
    config.read('server_config.ini')

    global session

    session = init_db(config['DataBase']['PATH'], config['DataBase']['BD_FILENAME'])

    app = QApplication(sys.argv)
    main = MainWindow(session)

    main.path_bd = config['DataBase']['PATH']
    main.file_name_bd = config['DataBase']['BD_FILENAME']

    PORT = parse_port_in_argv(sys.argv)
    ADDRES = parse_addres_in_argv(sys.argv)
    main.window3.lineEdit_4.setText(config['Server']['PORT'])
    main.window3.lineEdit_3.setText(config['Server']['ADDRES'])

    if PORT and PORT != config['Server']['PORT']:
        main.window3.lineEdit_4.setText(PORT)

    if ADDRES and ADDRES != config['Server']['ADDRES']:
        main.window3.lineEdit_3.setText(ADDRES)

    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
