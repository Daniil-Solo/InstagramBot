import json
import logging
import os
import pickle
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

    def authorizate(self, login, password, name):
        if login == '' or password == '':
            return False, "Ошибка: Одно из полей не заполнено"
        else:
            self._login, self._password = login, password
        try:
            if self._browser is None:
                self._browser = webdriver.Chrome(ChromeDriverManager().install())
            self._browser.get(url='https://www.instagram.com/')
        except WebDriverException:
            self._browser = None
            return False, "Ошибка: Отсутствует подключение к интернету"

        try:
            cookies = pickle.load(open(os.path.join('Source', 'sessions', name + '.pkl'), "rb"))
            cookies = cookies[0]
            if cookies:
                self._browser.add_cookie(cookies)
                self._browser.refresh()
                self.remove_notification()
                if self.is_auth_success():
                    return True, "Вход выполнен успешно"
                else:
                    pass
        except FileNotFoundError:
            pass

        time.sleep(3)
        self.fill_login_and_password_and_press_enter()
        time.sleep(3)

        try:
            self._browser.find_element_by_class_name('eiCW-')
            self.close_browser()
            self._browser = None
            return False, "Ошибка: Неправильный логин или пароль"
        except NoSuchElementException:
            cookies = self._browser.get_cookie('sessionid')
            if cookies:
                pickle.dump([cookies], open(os.path.join('Source', 'sessions', name + '.pkl'), "wb"))
                print(cookies)
            return True, "Вход выполнен успешно"

    def remove_notification(self):
        try:
            notification_panel = self._browser.find_element_by_class_name('mt3GC')
            button = notification_panel.find_elements_by_tag_name("button")[1]
            button.click()
        except NoSuchElementException:
            pass
        return

    def is_auth_success(self):
        try:
            self._browser.find_element_by_class_name("cGcGK")
            return True
        except NoSuchElementException:
            return False

    def close_browser(self):
        self._browser.close()
        self._browser.quit()

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
