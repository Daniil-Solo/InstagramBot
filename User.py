import time

from selenium.common.exceptions import NoSuchElementException


class User:
    def __init__(self, name, browser=None):
        self._name = name
        self._browser = browser
        self.n_subscribers = None
        self.n_posts = None
        self.open_user_page()

    def get_description(self) -> str:
        time.sleep(2)
        description_block = self._browser.find_element_by_class_name("-vDIg")
        header = self._get_header(description_block)
        text = self._get_text(description_block)
        return header + text

    @staticmethod
    def _get_header(description_block) -> str:
        try:
            header = description_block.find_element_by_tag_name('h1').text
        except NoSuchElementException:
            header = ''
        return header

    @staticmethod
    def _get_text(description_block) -> str:
        text = ' '
        try:
            items = description_block.find_elements_by_tag_name('span')
            for item in items:
                if "Подписан" not in item.text:
                    text += " " + item.text
                else:
                    break
        except NoSuchElementException:
            pass
        return text

    def is_correct(self):
        return self._is_page_exist() and self._is_opened()

    def open_user_page(self, time_out=1):
        if self._browser:
            new_url = f"https://www.instagram.com/{self._name}/"
            self._browser.get(new_url)
            time.sleep(time_out)

    def get_n_post(self):
        if self.n_posts is None:
            if self._has_posts():
                string_n_post = self._browser.find_element_by_xpath(
                    '/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span'
                ).text
                n_post = self.number_n_sub(string_n_post)
                self.n_posts = n_post
                return n_post
            else:
                self.n_posts = 0
                return 0
        else:
            return self.n_posts

    def get_n_subscribers(self):
        if self.n_subscribers is None:
            try:
                string_n_subscribers = self._browser.find_element_by_xpath(
                    '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span').text
            except:
                string_n_subscribers = self._browser.find_element_by_xpath(
                    '/html/body/div[1]/section/main/div/header/section/ul/li[2]/span/span').text
            n_subscribers = self.number_n_sub(string_n_subscribers)
            self.n_subscribers = n_subscribers
            return n_subscribers
        else:
            return self.n_subscribers

    @staticmethod
    def number_n_sub(string_n_subscribers):
        if 'тыс.' in string_n_subscribers:
            n_subscribers = int(float(string_n_subscribers[:-4].replace(',', '.')) * 1_000)
        elif 'млн' in string_n_subscribers:
            n_subscribers = int(float(string_n_subscribers[:-3].replace(',', '.')) * 1_000_000)
        else:
            n_subscribers = int(string_n_subscribers.replace(' ', ''))
        return n_subscribers

    def _is_page_exist(self):
        wrong_xpath = '/html/body/div[1]/section/main/div/h2'
        return not self.xpath_exist(wrong_xpath)

    def _is_opened(self):
        wrong_xpath = '/html/body/div[1]/section/main/div/div/article/div[1]/div/h2'
        return not self.xpath_exist(wrong_xpath)

    def _has_posts(self):
        wrong_xpath = '/html/body/div[1]/section/main/div/div[2]/article/div[1]/div/div[2]/h1'
        return not self.xpath_exist(wrong_xpath)

    def is_error_wait_some_minutes(self):
        wrong_xpath = '/html/body/div/div[1]/div/div'
        return self.xpath_exist(wrong_xpath)

    def xpath_exist(self, xpath):
        try:
            self._browser.find_element_by_xpath(xpath)
            exist = True
        except:
            exist = False
        return exist
