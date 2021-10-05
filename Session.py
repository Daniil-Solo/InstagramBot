import json
import time

from Master import Master
from Subscriber import Subscriber
from User import User


class Session:
    def __init__(self, parameters=None, browser=None):
        self._parameters = parameters
        self._browser = browser
        self.users = []
        self.unliked_users = []
        self.liked_users = []

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
            return True, "Сбор завершен успешно"
        except Exception as ex:
            return False, "Ошибка: " + str(ex)

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
                            if count == self._parameters["n_people"]:
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
        n_clients = self._parameters["n_people"]
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
        self.save_collected_users()
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

    def save_collected_users(self):
        file_name = self._parameters['file_name']
        with open(file_name, 'w') as write_file:
            for user in self.unliked_users:
                write_file.write(user + '\n')

    def save_unliked_users(self):
        unliked_clients_set = set()
        try:
            with open('Source/unliked_users.txt', "r") as read_file:
                unliked_clients_set = read_file.readlines()
                unliked_clients_set = [user.strip() for user in unliked_clients_set if user.strip() != '']
                unliked_clients_set = set(unliked_clients_set)
        except FileNotFoundError:
            pass
        finally:
            for user in self.unliked_users:
                unliked_clients_set.add(user)
            with open('Source/unliked_users.txt', 'w') as write_file:
                for user in unliked_clients_set:
                    write_file.write(user + '\n')

    def save_liked_users(self):
        liked_clients_set = set()
        try:
            with open('Source/liked_users.txt', "r") as read_file:
                liked_clients_set = read_file.readlines()
                liked_clients_set = [user.strip() for user in liked_clients_set if user.strip() != '']
                liked_clients_set = set(liked_clients_set)
        except FileNotFoundError:
            pass
        finally:
            for user in self.liked_users:
                liked_clients_set.add(user)
            with open('Source/liked_users.txt', 'w') as write_file:
                for user in liked_clients_set:
                    write_file.write(user + '\n')
