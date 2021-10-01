import json
import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


class Authorizator:
    def __init__(self):
        self._browser = None
        self._login = None
        self._password = None

    def authorizate(self, login, password):

        if login == '' or password == '':
            return False, "Одно из полей не заполнено"
        else:
            self._login, self._password = login, password
        try:
            if self._browser is None:
                self._browser = webdriver.Chrome(ChromeDriverManager().install())
            self._browser.get(url='https://www.instagram.com/')
        except WebDriverException:
            return False, "Отсутствует подключение к интернету"

        time.sleep(3)
        self.fill_login_and_password_and_press_enter()
        time.sleep(3)

        try:
            self._browser.find_element_by_class_name('eiCW-')
            self.close_browser()
            self._browser = None
            return False, "Неправильный логин или пароль"
        except NoSuchElementException:
            self.save_authorization_data()
            return True, "Вход выполнен успешно"

    def close_browser(self):
        self._browser.close()
        self._browser.quit()

    def save_authorization_data(self):
        data = {
            "login": self._login,
            "password": self._password
        }
        with open('Source/authorization.json', "w") as write_file:
            json.dump(data, write_file)

    def fill_login_and_password_and_press_enter(self, time_out=1):
        username_input = self._browser.find_element_by_name('username')
        username_input.clear()
        username_input.send_keys(self._login)
        time.sleep(time_out)
        password_input = self._browser.find_element_by_name('password')
        password_input.clear()
        password_input.send_keys(self._password)
        time.sleep(time_out)
        password_input.send_keys(Keys.ENTER)
        time.sleep(time_out)

    def get_browser(self):
        return self._browser
