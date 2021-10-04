import json
import time

from Master import Master
from Subscriber import Subscriber
from User import User


class Session:
    def __init__(self, parameters=None, browser=None):
        self._parameters = parameters
        self._browser = browser
        self.users = None
        self.unliked_users = None
        self.liked_users = None

    def generate_subscribers(self, size=1):
        try:
            master_name, master_status, message = self.get_master()
            if not master_status:
                return False, message

            master = Master(master_name, self._browser)
            all_parsed_clients, potential_clients_status, message = master.get_clients(size)
            if not all_parsed_clients:
                return False, message
            self.users = all_parsed_clients
            return True, ""
        except Exception as ex:
            return False, str(ex)

    def like_generated_users(self):
        count = 0
        full = False
        self.unliked_users = []
        self.liked_users = []
        for client_name in self.users:
            time.sleep(5)
            try:
                client = Subscriber(client_name, self._browser)
                if client.is_correct():
                    if not full:
                        if client.is_unique() and client.satisfies_parameters(self._parameters):
                            client.get_post(mode="actual")
                            client.like_posts(self._parameters)
                            self.liked_users.append(client_name)
                            time.sleep(self._parameters['timeout'])
                            count += 1
                            if count == self._parameters["n_potential_clients"]:
                                full = True
                    else:
                        self.unliked_users.append(client_name)
            except Exception:
                pass
        self.save_unliked_users()
        self.save_liked_users()
        return True, ""

    def like_collected_users(self, counter):
        count = 0
        counter.set(count)
        full = False
        n_clients = self._parameters["n_potential_clients"]
        self.unliked_users = []
        self.liked_users = []
        for client_name in self.users:
            if full:
                self.unliked_users.append(client_name)
                continue
            try:
                client = Subscriber(client_name, self._browser)
                if client.is_correct():
                    if client.is_unique() and client.satisfies_parameters(self._parameters):
                        client.get_post(mode="actual")
                        client.like_posts(self._parameters)
                        self.liked_users.append(client_name)
                        count += 1
                        counter.set(100 * count / n_clients)
                        if count == n_clients:
                            full = True
                        time.sleep(self._parameters['timeout'])
            except Exception:
                pass
            time.sleep(5)
        self.save_unliked_users2()
        self.save_liked_users()
        return True, "Лайки были успешно проставлены"

    def get_master(self):
        try:
            with open("source/masters.txt", "r") as f:
                masters = []
                for line in f:
                    if line != '':
                        masters.append(line)
        except FileNotFoundError:
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

    def save_unliked_users(self):
        unliked_clients_dict = dict()
        try:
            with open('Source/unliked_users.json', "r") as read_file:
                unliked_clients_dict = json.load(read_file)
        except FileNotFoundError:
            pass
        finally:
            for user in self.unliked_users:
                unliked_clients_dict[user] = 1
            with open('Source/unliked_users.json', "w") as write_file:
                json.dump(unliked_clients_dict, write_file)

    def save_unliked_users2(self):
        print("unliked")
        unliked_clients_dict = dict()
        for user in self.unliked_users:
            unliked_clients_dict[user] = 1
        with open('Source/unliked_users.json', "w") as write_file:
            json.dump(unliked_clients_dict, write_file)

    def save_liked_users(self):
        print("liked")
        liked_clients_dict = dict()
        try:
            with open('Source/liked_users.json', "r") as read_file:
                liked_clients_dict = json.load(read_file)
        except FileNotFoundError:
            pass
        finally:
            for user in self.liked_users:
                liked_clients_dict[user] = 1
            with open('Source/liked_users.json', "w") as write_file:
                json.dump(liked_clients_dict, write_file)
