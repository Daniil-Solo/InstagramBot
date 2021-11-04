import random
import time

from selenium.common.exceptions import NoSuchElementException

from Master import Master
from Subscriber import Subscriber
from User import User
from description_analysis import is_our_client, is_master, is_specific_master

import logging

from service_functions import save_statistics

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
        try:
            master_name, master_status, message = self.get_master()
            if not master_status:
                return False, message
            master = Subscriber(master_name, self._browser)
            logging.info(f"Master is {master_name}")
            posts = master.get_post()[:self._parameters['n_posts']]
            n_without_error_posts = len(posts)
            user_freq_dict = dict()

            for index, post_url in enumerate(posts):
                try:
                    post_likers = set()
                    self._browser.get(post_url)
                    time.sleep(3)
                    like_info_block = self._browser.find_element_by_xpath("/html/body/div[1]/section/main/div/div[1]/"
                                                                "article/div/div[2]/div/div[2]/section[2]/div/div/a")
                    if like_info_block.text == "":
                        like_info_block = self._browser.find_element_by_xpath("/html/body/div[1]/section/main/div/"
                                                "div[1]//article/div/div[2]/div/div[2]/section[2]/div/div[2]/a/span")

                    text_number = ""
                    for letter in like_info_block.text:
                        if letter.isdigit():
                            text_number += letter
                    n_users = int(text_number)

                    like_info_block.click()
                    time.sleep(3)

                    try:
                        liked_users_panel = self._browser.find_element_by_xpath("/html/body/div[6]/div/div/div[2]/div")
                    except NoSuchElementException:
                        liked_users_panel = self._browser.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div")
                    print(str(index + 1) + f" of {len(posts)}")

                    for _ in range(max(1, n_users // 17)):
                        time.sleep(random.randrange(3, 4))
                        self._browser.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollHeight", liked_users_panel
                        )
                        time.sleep(5)
                        users_block = self._browser.find_element_by_xpath("/html/body/div[6]/div/div/div[2]/div/div")
                        user_blocks = users_block.find_elements_by_tag_name('a')
                        users = [user_block.get_attribute('title') for user_block in user_blocks if
                                 user_block.get_attribute('title') != '']
                        print(users[:3])
                        for user in users:
                            post_likers.add(user)

                        for liker in post_likers:
                            if liker in user_freq_dict:
                                user_freq_dict[liker] += 1
                            else:
                                user_freq_dict[liker] = 1
                except Exception as ex:
                    print(ex)
                    n_without_error_posts = n_without_error_posts - 1
                time.sleep(20)

            user_freq_list = []
            for user_name in user_freq_dict:
                user_and_freq = (user_name, user_freq_dict[user_name] / n_without_error_posts)
                user_freq_list.append(user_and_freq)

            collected_users = self.get_active_likers(user_freq_list, threshold=self._parameters['freq'])
            with open(self._parameters['file_name'], 'a') as write_file:
                for user in collected_users:
                    write_file.write(user + '\n')
            return True, "Сбор завершен успешно"
        except Exception as ex:
            return False, "Ошибка: " + str(ex)

    @staticmethod
    def get_active_likers(user_freq_list, threshold=0):
        active_likers = []
        for user, freq in user_freq_list:
            if freq >= threshold:
                active_likers.append(user)
        return active_likers

    def collect_subscribers(self):
        size = self._parameters.get('percent_people') or 1
        try:
            master_name, master_status, message = self.get_master()
            if not master_status:
                return False, message

            master = Master(master_name, self._browser)
            logging.info(f"Master is {master_name}")
            logging.info(f"Goal is {int(master.get_n_subscribers() * size)} subscribers")
            all_parsed_clients, potential_clients_status, message = master.get_clients(size=size)
            if not all_parsed_clients:
                return False, message
            self.save_users([master_name], 'Source/parsed_masters.txt')
            self._users = all_parsed_clients
            self.save_users(self._users, self._parameters.get('file_name'))
            return True, "Сбор завершен успешно"
        except Exception as ex:
            return False, "Ошибка: " + str(ex)

    def like_collected_users(self) -> (bool, str):
        self._users = self.read_users_from_file(self._parameters.get('file_name'))
        if not self._users:
            logging.warning("Liking collected subscribers is failed")
            return False, "Ошибка: файл " + self._parameters.get('file_name') + " не найден или пуст!"

        liked_users = []
        unliked_users = []
        count = 0
        error_count = 0
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
                    logging.info(f"Like {client_name} - {str(count)}/{str(n_clients)}")
                    if count == n_clients:
                        break
                    time.sleep(self._parameters['timeout'])
                else:
                    time.sleep(5)
            except Exception:
                unliked_users.append(client_name)
                error_count += 1
                if error_count >= 2:
                    break
                continue

        self.write_users_to_file(self._users + unliked_users, self._parameters['file_name'])
        self.save_users(liked_users, "Source/liked_users.txt")
        return True, "Лайки были успешно проставлены"

    def filter_subscribers_with_ai(self) -> (bool, str):
        return False, "Данный метод не определен"

    def filter_subscribers(self) -> (bool, str):
        self._users = self.read_users_from_file(self._parameters.get('input_file_name'))
        if not self._users:
            return False, "Ошибка: файл " + self._parameters.get('input_file_name') + " не найден или пуст!"

        for_liking_users = []
        error_count = 0

        all_count = 0
        count = 0
        closed_count = 0
        master_count = 0
        not_our_client_count = 0
        not_in_range_count = 0
        not_post_count = 0
        n_clients = self._parameters["n_people"]
        while self._users:
            print("\n")
            client_name = self._users.pop()
            print("Клиент: " + client_name)
            all_count += 1
            try:
                client = Subscriber(client_name, self._browser)
                if client.is_error_wait_some_minutes():
                    print("Ошибка! Требуется подождать")
                    logging.warning(f"TimeError. Finish result: {count}/{n_clients}")
                    break
                time.sleep(2)
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
                    error_count = 0
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
                            if master.has_specific_name() or is_specific_master(description):
                                self.save_users([client_name], 'Source/masters.txt')
                                print("Добавляем в базу данных мастеров")
                                master_count += 1
                            else:
                                print("Похоже, что он не занимается эпосикдными урашениями")
                            for_liking_users.append(client_name)
                            count += 1
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
                    logging.info(f"Add {client_name} - {str(count)}/{str(n_clients)}")
                    if count == n_clients:
                        break
                    time.sleep(self._parameters['timeout'])
            except Exception as ex:
                error_count += 1
                print(f"Глобальная ошибка! {ex}")
                time.sleep(10)
                if error_count > 2:
                    self._users.append(client_name)
                    print("Ошибка! Превышено число ошибочных попыток")
                    logging.warning(f"CountError. Finish result: {count}/{n_clients}")
                    break
                else:
                    continue

        save_statistics(
            [all_count, count, closed_count, master_count, not_our_client_count, not_in_range_count, not_post_count])
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
