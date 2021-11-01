import sys
import json
from yaml import load, SafeLoader
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow
from threading import Thread

from interface_data import InterfaceDataManger, InterfaceDataMangerThread
from ParametersManager import ParametersManager
from service_functions import get_account
from tasks import *
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
        self.parameters_manager = ParametersManager(init_mode=-1)
        self.account_counter = 0
        self.idm = InterfaceDataManger()
        self.start_interface_data_updating_thread()
        self.elements = dict()
        self.start_load()
        self.all_connection()
        self.autofill()
        logging.info("")
        logging.info("Launching the application")

    # -----------Label, Buttons, ProgressBar--------
    def start_interface_data_updating_thread(self):
        self.idm.save_data()
        thread = InterfaceDataMangerThread(self)
        thread.start()
        thread.STATUS.connect(self.update_interface_data)

    def update_interface_data(self, global_status):
        data = global_status.split('#')
        status = data.pop(0)
        if status[0] == 's':
            self.label.setStyleSheet("color: green;")
        elif status[0] == 'e':
            self.label.setStyleSheet("color: red;")
        elif status[0] == 'i':
            self.label.setStyleSheet("color: black;")
        else:
            return
        self.label.setText(status[1:])

        progress = int(data.pop(0))
        self.progressBar.setValue(progress)

        blocked_elements = data
        self.set_elements(blocked_elements)

    def set_elements(self, blocked_elements):
        for element in self.elements:
            self.elements[element].setEnabled(True)

        for element in blocked_elements:
            if element:
                self.elements[element].setEnabled(False)

    # -----------Start-----------------
    def start_load(self):
        self.idm.block_start_elements()
        self.parameters_textbox.setPlainText("Параметры недоступны")
        # Authorization
        self.elements['lgn'] = self.login
        self.elements['psw'] = self.password
        self.elements['aub'] = self.authorize_button
        self.elements['nub'] = self.next_user_button
        # Top buttons
        self.elements['cmb'] = self.change_mode_button
        # Processing
        self.elements['upb'] = self.update_parameters_button
        self.elements['stb'] = self.start_button
        self.elements['spb'] = self.stop_button

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

    def all_connection(self):
        self.authorize_button.clicked.connect(self.handle_authorizate)
        self.start_button.clicked.connect(self.handle_start)
        self.close_button.clicked.connect(self.handle_close)
        self.update_parameters_button.clicked.connect(self.handle_update_parameters)
        self.change_mode_button.clicked.connect(self.handle_change_mode)
        self.next_user_button.clicked.connect(self.change_filling_data)
        self.stop_button.clicked.connect(self.handle_stop)

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
        login = self.login.text()
        password = self.password.text()
        th = Thread(target=self.authorizate, args=(login, password))
        th.start()

    def handle_start(self):
        th1 = Thread(target=self.start_work)
        th1.start()

    def handle_stop(self):
        self.idm.stop_process()

    # --------Main functions---------
    def authorizate(self, login, password):
        logging.info("Starting authorization")
        self.idm.set_message('Выполняется вход в аккаунт, пожалуйста подождите')
        self.idm.block_auth_elements()
        authorization_status, message = self.my_bot.authorizate(login, password)
        self.idm.set_message(message, authorization_status)

        if authorization_status:
            self.idm.deblock_elements()
            logging.info("Authorization is OK")
        else:
            self.idm.block_process_elements()
            logging.warning("Authorization is failed")

    def start_work(self):
        self.idm.block_process_elements()

        browser = self.my_bot.get_browser()
        my_session = Session(self.parameters_manager.parameters, browser, self.idm)

        if self.parameters_manager.check_mode(0):
            self.idm.set_message('Выполняется сбор подписчиков, пожалуйста подождите')
            logging.info("Start collecting subscribers")
            generation_status, message = my_session.collect_subscribers()
            self.idm.set_message(message, generation_status)
            logging.info(f"Real result is {len(my_session.get_users())} subscribers")
            if generation_status:
                logging.info(
                    f"The collected users were saved to {self.parameters_manager.parameters.get('file_name')}")
                logging.info("Collecting subscribers is OK")
            else:
                logging.warning("Collecting subscribers is failed")

        elif self.parameters_manager.check_mode(1):
            self.idm.set_message('Выполняется фильтрация подписчиков, пожалуйста подождите')
            logging.info("Start filter for collected subscribers")
            collected_users = my_session.read_users_from_file(self.parameters_manager.parameters.get('input_file_name'))
            my_session.set_users(collected_users)
            status, message = my_session.filter_subscribers()
            self.idm.set_message(message, status)
            if status:
                logging.info("Filter collected subscribers is OK")
            else:
                logging.warning("Filter collected subscribers is failed")

        elif self.parameters_manager.check_mode(2):
            self.idm.set_message('Выполняется лайкинг собранных подписчиков, пожалуйста подождите')
            logging.info("Start liking collected subscribers")
            liking_status, message = my_session.like_collected_users()
            self.idm.set_message(message, liking_status)
            if liking_status:
                logging.info("Liking collected subscribers is OK")
            else:
                logging.warning("Liking collected subscribers is failed")

        self.idm.restart_stop_status()
        self.idm.deblock_elements()


if __name__ == "__main__":
    task_on = True
    if not task_on:
        app = QApplication(sys.argv)
        window = HomeWindow()
        window.show()
        sys.exit(app.exec_())
    else:
        task_configs = load(open("schedule.yml"), Loader=SafeLoader).get("tasks")
        seq = TaskSequence()
        for task_config in task_configs:
            task_name = task_config.get("alias")
            account = get_account(task_name)
            task_type = task_config.get("type")
            seq.create_and_add_task(account, task_name, task_type)
        seq.run()
