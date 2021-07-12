import json
import random
import time

from User import User


class Subscriber(User):
    def __init__(self, name, browser):
        super().__init__(name, browser)
        self.posts = None

    def is_unique(self):
        try:
            with open('Source/liked_users.json', "r") as read_file:
                liked_clients_dict = json.load(read_file)
            if self._name in liked_clients_dict:
                return False
            else:
                return True
        except FileNotFoundError:
            return True

    def satisfies_parameters(self, parameters):
        self.get_n_subscribers()
        lower_border, upper_border = parameters["popularity"]
        return self._has_posts() and lower_border <= self.n_subscribers <= upper_border

    def get_post(self, mode="actual"):
        if self.posts is None:
            loop_count = 0
            if mode == "actual":
                pass
            elif mode == "all":
                loop_count = self.get_n_post() // 12

            for _ in range(loop_count):
                self._browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.randrange(3, 4))

            hrefs = self._browser.find_elements_by_tag_name('a')
            post_urls = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]
            self.posts = post_urls
            return post_urls
        else:
            return self.posts

    def like_posts(self, parameters):
        n_likes = parameters['n_likes']
        like_mode = parameters['like_mode']

        if n_likes > self.get_n_post():
            n_likes = self.get_n_post()
        if like_mode == 0:
            self.like_first_posts(n_likes)
        elif like_mode == 1:
            self.like_last_posts(n_likes)
        else:
            self.like_random_posts(n_likes)

    def like_first_posts(self, n_post):
        for post_url in self.get_post()[:n_post]:
            self.like_this_post(post_url)

    def like_last_posts(self, n_post):
        for post_url in self.get_post()[-n_post:]:
            self.like_this_post(post_url)

    def like_random_posts(self, n_post):
        random_sample = random.choices(population=self.get_post(), k=n_post)
        for post_url in random_sample:
            self.like_this_post(post_url)

    def like_this_post(self, post_url):
        self._browser.get(post_url)
        time.sleep(2)
        like_button = '/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[' \
                      '1]/button'
        self._browser.find_element_by_xpath(like_button).click()
        time.sleep(2)
