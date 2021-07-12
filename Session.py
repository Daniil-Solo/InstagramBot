import time

from Master import Master
from Subscriber import Subscriber
from User import User


class Session:
    def __init__(self, parameters, browser):
        self._parameters = parameters
        self._browser = browser
        self.potential_clients = None

    def generate_potential_clients(self):
        try:
            master_name, master_status, message = self.get_master()
            if not master_status:
                return False, message

            master = Master(master_name, self._browser)
            potential_clients, potential_clients_status, message = master.get_potential_clients(self._parameters)
            if not potential_clients_status:
                return False, message
            self.potential_clients = potential_clients
            return True, ""
        except Exception as ex:
            return False, str(ex)

    def like_generated_users(self, main):
        count = 0
        n = len(self.potential_clients)
        for client_name in self.potential_clients:
            client = Subscriber(client_name, self._browser)
            client.get_post(mode="actual")
            client.like_posts(self._parameters)
            time.sleep(self._parameters['timeout'])
            count += 1
            main.process(int(count/n*100))
            time.sleep(1)
        return True, ""

    def get_master(self):
        try:
            with open("source/masters.txt", "r") as f:
                masters = []
                for line in f:
                    if line != '':
                        masters.append(line)
        except:
            return None, False, "Отсутствует файл master.txt"
        if not masters:
            return None, False, "Файл master.txt пуст"
        stop = False
        master_name = ""

        while not stop:
            if not masters:
                return None, False, "Нет подходящего мастера в файле master.txt"
            master_name = masters.pop(0)
            master = User(master_name, self._browser)
            if master.is_correct():
                stop = True

        with open("source/masters.txt", "w") as f:
            for item in masters:
                f.write(item)
        return master_name, True, ""
