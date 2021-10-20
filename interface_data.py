from PyQt5 import QtCore
from PyQt5.QtCore import QThread


class InterfaceDataMangerThread(QThread):
    STATUS = QtCore.pyqtSignal(str)

    def run(self):
        while True:
            val = get_interface_data()
            self.STATUS.emit(val)


def get_interface_data():
    try:
        with open('Source/interface_data.txt', 'r') as read_file:
            result = read_file.read()
    except FileNotFoundError:
        result = "i#0#"
    if not result:
        result = "i#0#"
    return result


class InterfaceDataManger:
    def __init__(self):
        self.message = "i"
        self.progress_value = 0
        self.blocked_elements = []

    def set_message(self, message, type_message=None):
        if type_message is None:
            self.message = "i"
        elif type_message:
            self.message = "s"
        else:
            self.message = "e"
        self.message += message
        self.save_data()

    def set_progress(self, value):
        self.progress_value = value
        self.save_data()

    def block_auth_elements(self):
        self.blocked_elements = ['lgn', 'psw', 'aub', 'upb', 'stb', 'cmb']
        self.save_data()

    def block_process_elements(self):
        self.blocked_elements = ['upb', 'stb', 'cmb']
        self.save_data()

    def deblock_elements(self):
        self.blocked_elements = []
        self.save_data()

    def save_data(self):
        data = self.message + "#" + str(int(self.progress_value))
        for button in self.blocked_elements:
            data += "#" + button
        with open('Source/interface_data.txt', 'w') as write_file:
            write_file.write(data)
