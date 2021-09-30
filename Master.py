import json
import time
import random

from User import User


class Master(User):
    def __init__(self, name, browser):
        super().__init__(name, browser)
        self.limit = 180

    def get_clients(self):
        try:
            self.get_n_subscribers()
            count_subscribers = self.limit
            if self.n_subscribers < self.limit:
                count_subscribers = self.n_subscribers
            self.scroll_down(count_subscribers)
            subscriber_names = self.find_subscribers_names()
            return subscriber_names, True, ""
        except Exception as ex:
            return [], False, str(ex)

    def find_subscribers_names(self):
        followers_block = self._browser.find_element_by_xpath('/html/body/div[6]/div/div/div[2]/ul/div')
        followers = followers_block.find_elements_by_class_name('wo9IH')
        follower_names = []
        for follower in followers:
            follower_url = follower.find_element_by_tag_name('a').get_attribute('href')
            follower_name = follower_url.split('/')[-2]
            follower_names.append(follower_name)
        return follower_names

    def scroll_down(self, count_subscribers):
        loop_count = max(count_subscribers, 12) // 12
        subs_button = '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span'
        self._browser.find_element_by_xpath(subs_button).click()
        time.sleep(2)
        followers_panel = self._browser.find_element_by_xpath('/html/body/div[6]/div/div/div[2]')
        for _ in range(loop_count):
            self._browser.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", followers_panel
            )
            time.sleep(random.randrange(4, 5))
