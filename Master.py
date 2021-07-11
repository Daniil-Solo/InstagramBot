from User import User


class Master(User):
    def __init__(self, name, browser):
        super().__init__(name, browser)

    def get_potential_clients(self, parameters):
        pass