from PyQt5 import QtCore
from PyQt5.QtCore import QThread


class Counter:
    def __init__(self):
        self.value = 0

    def set(self, value):
        self.value = value
        with open('Source/percent.txt', 'w') as write_file:
            write_file.write(str(value))


def get_value():
    try:
        with open('Source/percent.txt', 'r') as read_file:
            result = float(read_file.read())
    except ValueError:
        result = 0
    if result > 100:
        result = 100
    return result


class ThreadClass(QThread):
    PROGRESS = QtCore.pyqtSignal(float)

    def run(self):
        while True:
            val = get_value()
            self.PROGRESS.emit(val)