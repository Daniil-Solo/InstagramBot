import sys
import time
import json

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox
from threading import Thread

from Authorizator import Authorizator
from Session import Session
from ProgressBar import *
from ParametersManager import ParametersManager


class HomeWindow(QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()
        loadUi("Interface/MainWindow.ui", self)
        self.my_bot = Authorizator()
        self.parameters_manager = ParametersManager(init_mode=0)
        self.counter = Counter()
        self.start_progress_thread()
        self.start_load()
        self.all_connection()
        self.autofill()

# ------------Progress bar-------------
    def start_progress_thread(self):
        self.counter.set(0)
        thread = ThreadClass(self)
        thread.start()
        thread.PROGRESS.connect(self.updateProgressBar)

    def updateProgressBar(self, val):
        self.progressBar.setValue(int(val))

# -----------Start-----------------
    def start_load(self):
        for element in [self.update_parameters_button, self.start_button, self.progressBar, self.change_mode_button]:
            element.setEnabled(False)
        self.parameters_textbox.setPlainText("Войдите в аккаунт")

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

    def show_info(self, status, message):
        if status:
            self.label.setStyleSheet("color: green;")
        else:
            self.label.setStyleSheet("color: red;")
        self.label.setText(message)

    def all_connection(self):
        self.authorize_button.clicked.connect(self.handle_authorizate)
        self.start_button.clicked.connect(self.handle_start)
        self.close_button.clicked.connect(self.handle_close)
        self.update_parameters_button.clicked.connect(self.handle_update_parameters)
        self.change_mode_button.clicked.connect(self.handle_change_mode)

# ----------Handlers--------------
    def handle_change_mode(self):
        self.parameters_manager.next_mode()
        self.parameters_textbox.setPlainText(self.parameters_manager.get_text_parameters())

    def handle_update_parameters(self):
        text = self.parameters_manager.get_text_parameters()
        self.parameters_textbox.setPlainText(text)

    def handle_close(self):
        self.my_bot.close_browser()
        self.close()
        self.quit()

    def handle_authorizate(self):
        th = Thread(target=self.authorizate)
        th.start()

    def handle_start(self):
        th1 = Thread(target=self.start_work)
        th1.start()

# --------Main functions---------
    def authorizate(self):
        self.label.setStyleSheet("color: black;")
        self.label.setText('Выполняется вход в аккаунт, пожалуйста подождите')
        self.label.show()
        for element in [self.parameters_textbox, self.login, self.password, self.authorize_button]:
            element.setEnabled(False)
        login = self.login.text()
        password = self.password.text()
        authorization_status, message = self.my_bot.authorizate(login, password)
        self.show_info(authorization_status, message)

        for element in [self.parameters_textbox, self.update_parameters_button, self.start_button,
                        self.progressBar,  self.change_mode_button]:
            element.setEnabled(authorization_status)

        for element in [self.login, self.password, self.authorize_button]:
            element.setEnabled(True)

        if authorization_status:
            self.handle_update_parameters()

    def start_work(self):
        for element in [self.update_parameters_button, self.start_button, self.authorize_button,
                        self.login, self.password, self.change_mode_button]:
            element.setEnabled(False)

        browser = self.my_bot.get_browser()
        my_session = Session(self.parameters_manager.parameters, browser)

        if self.parameters_manager.check_mode(0):
            status, message = my_session.generate_subscribers()
            if status:
                status, message = my_session.like_generated_users()
            self.show_info(status, message)

        elif self.parameters_manager.check_mode(1):
            generation_status, message = my_session.generate_subscribers(
                size=self.parameters_manager.parameters.get('percent_people'))
            self.show_info(generation_status, message)

            file_name = self.parameters_manager.parameters.get('file_name')
            with open(file_name, 'a') as append_file:
                for user in my_session.users:
                    append_file.write(user + '\n')

        elif self.parameters_manager.check_mode(2):
            file_name = self.parameters_manager.parameters.get('file_name')
            with open(file_name, 'r') as read_file:
                collected_users = list(set(read_file.readlines()))

            my_session.users = collected_users
            liking_status, message = my_session.like_collected_users(self.counter)
            self.show_info(liking_status, message)

        for element in [self.update_parameters_button, self.start_button, self.authorize_button,
                        self.login, self.password, self.change_mode_button]:
            element.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())
