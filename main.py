import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox

from InstagramBot import InstagramBot
from Session import Session


class HomeWindow(QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()
        loadUi("Interface/MainWindow.ui", self)
        self.my_bot = InstagramBot()
        self.parameters = dict()
        self.start_load()
        self.all_connection()

    def start_load(self):
        for element in [self.parameters_textbox, self.change_parameters_button, self.start_button, self.progressBar]:
            element.setEnabled(False)

    def all_connection(self):
        self.authorize_button.clicked.connect(self.handle_authorizate)
        self.start_button.clicked.connect(self.handle_start_like)

# обработчики
    def handle_authorizate(self):
        self.label.setText('Выполняется вход в аккаунт, пожалуйста подождите')
        for element in [self.login, self.password, self.authorize_button]:
            element.setEnabled(False)
        login = self.login.text()
        password = self.password.text()
        authorization_status, message = self.my_bot.authorizate(login, password)

        msg = QMessageBox()
        if authorization_status:
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Successfully")
        else:
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Error")
        msg.setText(message)
        msg.exec_()

        if authorization_status:
            for element in [self.parameters_textbox, self.change_parameters_button, self.start_button,
                            self.progressBar]:
                element.setEnabled(True)
        else:
            for element in [self.parameters_textbox, self.change_parameters_button, self.start_button,
                            self.progressBar]:
                element.setEnabled(False)
        for element in [self.login, self.password, self.authorize_button]:
            element.setEnabled(True)
        self.label.setText('')

    def handle_start_like(self):
        browser = self.my_bot.get_browser()
        my_session = Session(self.parameters, browser)
        generation_status, message = my_session.generate_potential_clients()
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeWindow()
    window.show()
    sys.exit(app.exec_())