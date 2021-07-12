import json
import time
import random

from Subscriber import Subscriber
from User import User


class Master(User):
    def __init__(self, name, browser):
        super().__init__(name, browser)
        self.limit = 10

    def get_clients(self):
        try:
            self.get_n_subscribers()
            count_subscribers = self.limit
            if self.n_subscribers < self.limit:
                count_subscribers = self.n_subscribers
            self.scroll_down(count_subscribers)
            subscriber_names = self.find_subscribers_urls()
            return subscriber_names, True, ""
        except Exception as ex:
            return [], False, str(ex)


    def find_subscribers_urls(self):
        followers_block = self._browser.find_element_by_xpath('/html/body/div[5]/div/div/div[2]/ul/div')
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
        followers_panel = self._browser.find_element_by_xpath('/html/body/div[5]/div/div/div[2]')
        for _ in range(loop_count):
            self._browser.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", followers_panel
            )
            time.sleep(random.randrange(4, 5))

    def open_liked_users(self):
        try:
            with open('Source/unliked_users.json', "r") as read_file:
                liked_clients_dict = json.load(read_file)
            return liked_clients_dict
        except:
            return dict()

"""
            potential_clients_names = []
            for subscriber_name in subscriber_names:
                subscriber = Subscriber(subscriber_name, self._browser)
                if subscriber.is_correct():
                    if subscriber.is_unique() and subscriber.satisfies_parameters(parameters):
                        potential_clients_names.append(subscriber_name)
                time.sleep(random.randrange(3, 6))
            n_real_potential_clients = len(potential_clients_names)
            n_parameters_potential_clients = parameters["n_potential_clients"]
            if n_parameters_potential_clients < n_real_potential_clients:
                self.save_unliked_potential_clients(potential_clients_names[n_parameters_potential_clients:])
                return potential_clients_names[:n_parameters_potential_clients], True, ""
            else:
                return potential_clients_names[:n_real_potential_clients], True, ""




"""