class User:
    def __init__(self, name, browser):
        self._name = name
        self._browser = browser
        self.n_subscribers = None
        self.n_posts = None

    def is_correct(self):
        pass
