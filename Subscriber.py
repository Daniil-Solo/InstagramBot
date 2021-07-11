import json

from User import User

class Subscriber(User):
    def __init__(self, name, browser):
        super().__init__(name, browser)

    def is_unique(self):
        try:
            with open('Source/unliked_users.json', "r") as read_file:
                liked_clients_dict = json.load(read_file)
            if self._name in liked_clients_dict:
                return False
            else:
                return True
        except:
            return True

    def satisfies_parameters(self, parameters):
        self.get_n_subscribers()
        poplularity = parameters["popularity"]
        return self._has_posts() and poplularity[0] <= self.n_subscribers <= poplularity[1]
