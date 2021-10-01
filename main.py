import sys
import time
import json

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox
from threading import Thread

from Authorizator import Authorizator
from Session import Session


class HomeWindow(QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()
        loadUi("Interface/MainWindow.ui", self)
        self.my_bot = Authorizator()
        self.parameters = None
        self.start_load()
        self.all_connection()
        self.autofill()
        self.show_parameters()

    def start_load(self):
        for element in [self.collect_subscribers_button, self.start_button, self.progressBar]:
            element.setEnabled(False)

        try:
            with open('Source/parameters.json', 'r') as read_file:
                self.parameters = json.load(read_file)
        except FileNotFoundError:
            self.parameters = {
                "n_potential_clients": 60,
                "n_likes": 1,
                "timeout": 60,
                "like_mode": 0,
                "popularity": [100, 500]
            }
            with open('Source/parameters.json', 'w') as write_file:
                json.dump(self.parameters, write_file)

    def autofill(self):
        try:
            with open('Source/authorization.json', 'r') as read_file:
                auth_parameters = json.load(read_file)
            self.login.setText(auth_parameters['login'])
            self.password.setText(auth_parameters['password'])
        except FileNotFoundError:
            return
        except TypeError:
            self.login.setText("")
            self.password.setText("")

    def show_parameters(self):
        text = "Параметры отсутствуют"
        try:
            with open('Source/parameters_view.txt', 'r', encoding='UTF-8') as read_file:
                text_lines = read_file.readlines()
            text = ""
            for param, line in zip(self.parameters, text_lines):
                text += line.strip() + " " + str(self.parameters[param]) + '\n'
        except FileNotFoundError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText("Отсутствует файл parameters_view.txt")
            msg.exec_()
        self.parameters_textbox.setPlainText(text)

    def all_connection(self):
        self.authorize_button.clicked.connect(self.handle_authorizate)
        self.start_button.clicked.connect(self.handle_start_like)
        self.close_button.clicked.connect(self.handle_close)
        self.collect_subscribers_button.clicked.connect(self.handle_collect_subscribers)

    def handle_collect_subscribers(self):
        th = Thread(target=self.collect_subscribers)
        th.start()

    def collect_subscribers(self):
        browser = self.my_bot.get_browser()
        my_session = Session(None, browser)
        generation_status, message = my_session.generate_subscribers()
        if generation_status:
            self.label.setStyleSheet("color: green;")
        else:
            self.label.setStyleSheet("color: red;")
            message = "Ошибка: " + message
        self.label.setText(message)

        with open('Source/unliked_users.json', 'r') as read_file:
            current_users = json.load(read_file)

        collect_users = set(current_users.keys) + set(my_session.users)

        user_dict = dict()
        for user in collect_users:
            user_dict[user] = 1

        with open('Source/unliked_users.json', 'w') as write_file:
            json.dump(user_dict, write_file)

    def handle_close(self):
        self.my_bot.close_browser()
        self.close()

    def handle_authorizate(self):
        th = Thread(target=self.authorizate)
        th.start()

    # обработчики
    def authorizate(self):
        self.label.setStyleSheet("color: black;")
        self.label.setText('Выполняется вход в аккаунт, пожалуйста подождите')
        self.label.show()
        for element in [self.parameters_textbox, self.login, self.password, self.authorize_button]:
            element.setEnabled(False)
        login = self.login.text()
        password = self.password.text()
        authorization_status, message = self.my_bot.authorizate(login, password)

        text = ""

        if authorization_status:
            for element in [self.parameters_textbox, self.collect_subscribers_button, self.start_button,
                            self.progressBar]:
                element.setEnabled(True)
            self.label.setStyleSheet("color: green;")
        else:
            for element in [self.parameters_textbox, self.collect_subscribers_button, self.start_button,
                            self.progressBar]:
                element.setEnabled(False)
            self.label.setStyleSheet("color: red;")

        for element in [self.login, self.password, self.authorize_button]:
            element.setEnabled(True)
        self.label.setText(text + message)

    def handle_start_like(self):
        browser = self.my_bot.get_browser()
        my_session = Session(self.parameters, browser)
        generation_status, message = my_session.generate_subscribers()
        if not generation_status:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
            msg.setText(message)
            msg.exec_()
        else:
            liking_status, message = my_session.like_generated_users()
            if not liking_status:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Error")
                msg.setText(message)
                msg.exec_()

    def process(self, i):
        self.progressBar.setValue(i)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())
