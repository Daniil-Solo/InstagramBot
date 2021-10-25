import time

from Master import Master
from Subscriber import Subscriber
from User import User
from description_analysis import is_our_client, is_master
from saving_descriprion import save_statistics

import logging

logging.basicConfig(filename='log.log', level=logging.INFO,
                    format='%(asctime)s * %(levelname)s * %(message)s')


class Session:
    def __init__(self, parameters=None, browser=None):
        self._parameters = parameters
        self._browser = browser
        self._users = []

    def set_users(self, users):
        self._users = users

    def get_users(self):
        return self._users

    def collect_active_users(self):
        return False, "This function is not available"

    def generate_subscribers(self, size=1, counter=None):
        try:
            master_name, master_status, message = self.get_master()
            if not master_status:
                return False, message

            master = Master(master_name, self._browser)
            logging.info(f"Master is {master_name}")
            logging.info(f"Goal is {int(master.get_n_subscribers() * size)} subscribers")
            all_parsed_clients, potential_clients_status, message = master.get_clients(size=size, counter=counter)
            if not all_parsed_clients:
                return False, message
            self.save_users([master_name], 'Source/parsed_masters.txt')
            self._users = all_parsed_clients
            return True, "Сбор завершен успешно"
        except Exception as ex:
            return False, "Ошибка: " + str(ex)


    def like_collected_users(self, counter) -> (bool, str):
        liked_users = []
        count = 0
        counter.set_progress(count)
        n_clients = self._parameters["n_people"]
        while self._users:
            client_name = self._users.pop()
            try:
                client = Subscriber(client_name, self._browser)
                time.sleep(2)
                if client.is_correct():
                    client.get_post(mode="actual")
                    client.like_posts(self._parameters)
                    liked_users.append(client_name)
                    count += 1
                    counter.set_progress(100 * count / n_clients)
                    logging.info(f"Like {client_name} - {str(count)}/{str(n_clients)}")
                    if count == n_clients:
                        break
                    time.sleep(self._parameters['timeout'])
                else:
                    time.sleep(5)
            except Exception:
                print(client_name)
                continue

        self.write_users_to_file(self._users, self._parameters['file_name'])
        self.save_users(liked_users, "Source/liked_users.txt")
        return True, "Лайки были успешно проставлены"

    def filter_subscribers(self, counter) -> (bool, str):
        for_liking_users = []
        error_count = 0

        all_count = 0
        count = 0
        closed_count = 0
        master_count = 0
        not_our_client_count = 0
        not_in_range_count = 0
        not_post_count = 0
        counter.set_progress(count)
        n_clients = self._parameters["n_people"]
        while self._users and counter.not_stop():
            print("\n")
            client_name = self._users.pop()
            print("Клиент: " + client_name)
            all_count += 1
            try:
                client = Subscriber(client_name, self._browser)
                if error_count > 3:
                    self._users.append(client_name)
                    print("Ошибка! Превышено число ошибочных попыток")
                    logging.warning(f"CountError. Finish result: {count}/{n_clients}")
                    break
                if client.is_error_wait_some_minutes():
                    print("Ошибка! Требуется подождать")
                    logging.warning(f"TimeError. Finish result: {count}/{n_clients}")
                    break
                time.sleep(2)
                error_count = 0
                if not client.is_correct():
                    print("Ошибка! Страница закрыта или не существет")
                    closed_count += 1
                    time.sleep(self._parameters['timeout'] // 2)
                    continue
                elif not client.is_unique():
                    print("Ошибка! Его уже лайкали")
                    time.sleep(self._parameters['timeout'] // 2)
                    continue
                elif not client.is_in_range_of_subscribers(self._parameters):
                    print("Ошибка! Не подходит по числу подписчиков")
                    not_in_range_count += 1
                    time.sleep(self._parameters['timeout'] // 2)
                    continue
                elif not client.has_posts():
                    print("Ошибка! Не имеет постов")
                    not_post_count += 1
                    time.sleep(self._parameters['timeout'] // 2)
                    continue
                elif client.get_n_post() < 5:
                    print("Ошибка! Меньше 5 постов")
                    time.sleep(self._parameters['timeout'] // 2)
                    continue
                else:
                    try:
                        description = client.get_description()
                    except Exception as ex:
                        print("Ошибка с описанием!" + str(ex))
                        time.sleep(100)
                        continue
                    print(description)
                    if is_master(description):
                        master = Master(client_name, self._browser)
                        logging.warning(f"{client_name} has a master description")
                        print("Это мастер!")
                        if master.is_unique():
                            self.save_users([client_name], 'Source/masters.txt')
                            print("Добавляем в базу данных мастеров")
                            master_count += 1
                            for_liking_users.append(client_name)
                            count += 1
                            counter.set_progress(100 * count / n_clients)
                            logging.info(f"Add {client_name} - {str(count)}/{str(n_clients)}")
                            if count == n_clients:
                                break
                            time.sleep(self._parameters['timeout'])
                        continue
                    if not is_our_client(description):
                        logging.warning(f"{client_name} has an inappropriate description")
                        not_our_client_count += 1
                        print("Не подходит!")
                        continue
                    print("Подходит!")
                    for_liking_users.append(client_name)
                    count += 1
                    counter.set_progress(100 * count / n_clients)
                    logging.info(f"Add {client_name} - {str(count)}/{str(n_clients)}")
                    if count == n_clients:
                        break
                    time.sleep(self._parameters['timeout'])
            except Exception as ex:
                error_count += 1
                print(f"Глобальная ошибка! {ex}")
                time.sleep(100)
                continue

        save_statistics([all_count, count, closed_count, master_count, not_our_client_count, not_in_range_count, not_post_count])
        self.write_users_to_file(self._users, self._parameters['input_file_name'])
        self.save_users(for_liking_users, self._parameters['output_file_name'])
        return True, "Пользователи были успешно отфильтрованы"

    def get_master(self) -> (str, bool, str):
        master_file_name = "Source/masters.txt"

        masters = self.read_users_from_file(master_file_name)
        if not masters:
            return "", False, "Файл master.txt пуст или отсутствует"

        while True:
            master_name = masters.pop(0)
            master = User(master_name, self._browser)
            if master.is_correct():
                break
            if not masters:
                return "", False, "Нет подходящего мастера в файле masters.txt"

        self.write_users_to_file(masters, master_file_name)
        return master_name, True, "Мастер был успешно найден"

    def save_users(self, new_users: list, file_name: str) -> None:
        old_users = self.read_users_from_file(file_name)
        full_user_set = set(old_users) | set(new_users)
        self.write_users_to_file(full_user_set, file_name)

    @staticmethod
    def read_users_from_file(file_name: str) -> list:
        try:
            with open(file_name, "r") as read_file:
                user_names = read_file.readlines()
            return [user_name.strip() for user_name in user_names if user_name.strip()]
        except FileNotFoundError:
            return []

    @staticmethod
    def write_users_to_file(users: list or set, file_name: str) -> None:
        with open(file_name, "w") as write_file:
            for user in users:
                write_file.write(user + '\n')
