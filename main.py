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

import logging
logging.basicConfig(filename='log.log', level=logging.INFO,
                    format='%(asctime)s * %(levelname)s * %(message)s')
wdm_loger = logging.getLogger('WDM')
wdm_loger.disabled = True


class HomeWindow(QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()
        loadUi("Interface/MainWindow.ui", self)
        self.my_bot = Authorizator()
        self.parameters_manager = ParametersManager(init_mode=0)
        self.account_counter = 0
        self.counter = Counter()
        self.start_progress_thread()
        self.start_load()
        self.all_connection()
        self.autofill()
        logging.info("")
        logging.info("Launching the application")

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
            self.login.setText(auth_parameters[0]['login'])
            self.password.setText(auth_parameters[0]['password'])
        except FileNotFoundError:
            return
        except TypeError:
            self.login.setText("")
            self.password.setText("")

    def change_filling_data(self):
        try:
            with open('Source/authorization.json', 'r') as read_file:
                auth_parameters = json.load(read_file)
            n_accounts = len(auth_parameters)
            self.account_counter += 1
            if self.account_counter >= n_accounts:
                self.account_counter = 0
            self.login.setText(auth_parameters[self.account_counter]['login'])
            self.password.setText(auth_parameters[self.account_counter]['password'])
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
        self.fix_position_butttons .clicked.connect(self.change_filling_data)

    # ----------Handlers--------------
    def handle_change_mode(self):
        self.parameters_manager.next_mode()
        self.parameters_textbox.setPlainText(self.parameters_manager.get_text_parameters())

    def handle_update_parameters(self):
        text = self.parameters_manager.get_text_parameters()
        self.parameters_textbox.setPlainText(text)

    def handle_close(self):
        logging.info("Closing the application")
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
        logging.info("Starting authorization")
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
                        self.progressBar, self.change_mode_button]:
            element.setEnabled(authorization_status)

        for element in [self.login, self.password, self.authorize_button]:
            element.setEnabled(True)

        if authorization_status:
            self.handle_update_parameters()
            logging.info("Authorization is OK")
        else:
            logging.warning("Authorization is failed")

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
            logging.info("Start collecting subscribers")
            generation_status, message = my_session.generate_subscribers(
                size=self.parameters_manager.parameters.get('percent_people'), counter=self.counter)
            self.show_info(generation_status, message)
            logging.info(f"Real result is {len(my_session.get_users())} subscribers")
            if generation_status:
                my_session.save_users(my_session.get_users(), self.parameters_manager.parameters.get('file_name'))
                logging.info(
                    f"The collected users were saved to {self.parameters_manager.parameters.get('file_name')}")
                logging.info("Collecting subscribers is OK")
            else:
                logging.warning("Collecting subscribers is failed")

        elif self.parameters_manager.check_mode(2):
            logging.info("Start liking collected subscribers")
            collected_users = my_session.read_users_from_file(self.parameters_manager.parameters.get('file_name'))
            if not collected_users:
                self.show_info(False, "Ошибка: файл " + self.parameters_manager.parameters.get('file_name') +
                               " не найден или пуст!")
                logging.warning("Liking collected subscribers is failed")
            else:
                my_session.set_users(collected_users)
                liking_status, message = my_session.like_collected_users(self.counter)
                self.show_info(liking_status, message)
                if liking_status:
                    logging.info("Liking collected subscribers is OK")
                else:
                    logging.warning("Liking collected subscribers is failed")

        elif self.parameters_manager.check_mode(3):
            status, message = my_session.collect_active_users()
            self.show_info(status, message)
            my_session.save_users(my_session.get_users(), self.parameters_manager.parameters.get('file_name'))

        elif self.parameters_manager.check_mode(4):
            logging.info("Start filter for collected subscribers")
            collected_users = my_session.read_users_from_file(self.parameters_manager.parameters.get('input_file_name'))
            my_session.set_users(collected_users)
            status, message = my_session.filter_subscribers(self.counter)
            self.show_info(status, message)
            if status:
                logging.info("Filter collected subscribers is OK")
            else:
                logging.warning("Filter collected subscribers is failed")

        for element in [self.update_parameters_button, self.start_button, self.authorize_button,
                        self.login, self.password, self.change_mode_button]:
            element.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())
