from Master import Master
from User import User


class Session:
    def __init__(self, parameters, browser):
        self._parameters = parameters
        self._browser = browser
        self.potential_clients = None

    def generate_potential_clients(self):
        master_name, master_status, message = self.get_master()
        if not master_status:
            return False, message

        master = Master(name=master_name, browser=self._browser)
        potential_clients, potential_clients_status, message = master.get_potential_clients(self._parameters)
        if not potential_clients_status:
            return False, message

        self.potential_clients = potential_clients
        return True, ""

    def like_generated_users(self):
        pass

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
