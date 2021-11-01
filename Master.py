import time
import random

from User import User


class Master(User):
    def __init__(self, name, browser):
        super().__init__(name, browser)

    def get_clients(self, size=1):
        try:
            self.get_n_subscribers()
            self.scroll_down(count_subscribers=int(self.n_subscribers * size))
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
        loop_count = min(count_subscribers // 12, 30)
        subs_button = '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span'
        self._browser.find_element_by_xpath(subs_button).click()
        time.sleep(2)
        followers_panel = self._browser.find_element_by_xpath('/html/body/div[6]/div/div/div[2]')
        for i in range(loop_count):
            self._browser.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", followers_panel
            )
            time.sleep(random.randrange(4, 5))

    def is_unique(self):
        try:
            with open('Source/parsed_masters.txt', "r") as read_file:
                parsed_masters_set = set([master.strip() for master in read_file.readlines()])
            if self._name in parsed_masters_set:
                return False
            else:
                return True
        except FileNotFoundError:
            return True

    def has_specific_name(self):
        specific_names = ['art', 'epoxy', 'flowers', 'ja', 'resinart', 'jewelry', 'resin', 'smola']
        for specific_part in specific_names:
            if specific_part in self._name:
                return True
        return False
