import time


class User:
    def __init__(self, name, browser):
        self._name = name
        self._browser = browser
        self.n_subscribers = None
        self.n_posts = None

    def is_correct(self):
        self.open_user_page()
        return self._is_page_exist and self._is_opened

    def open_user_page(self, time_out=1):
        new_url = f"https://www.instagram.com/{self._name}/"
        self._browser.get(new_url)
        time.sleep(time_out)

    def _is_page_exist(self):
        wrong_xpath = '/html/body/div[1]/section/main/div/h2'
        return not self.xpath_exist(wrong_xpath)

    def _is_opened(self):
        wrong_xpath = '/html/body/div[1]/section/main/div/div/article/div[1]/div/h2'
        return not self.xpath_exist(wrong_xpath)

    def xpath_exist(self, xpath):
        try:
            self._browser.find_element_by_xpath(xpath)
            exist = True
        except:
            exist = False
        return exist