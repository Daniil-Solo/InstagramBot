from abc import ABC, abstractmethod

from Authorizator import Authorizator
from Session import Session
from service_functions import get_parameters


def session_decorate(session_function):
    def wrapped(self):
        session = Session(parameters=self._parameters, browser=self._browser)
        status, msg = session_function(session)
        return TaskAnswer(message=msg, status=status)
    return wrapped


class TaskAnswer:
    def __init__(self, message: str, status=None):
        self._message = message
        self._status = status

    def get_message(self) -> str:
        return self._message

    def get_status(self) -> bool:
        return self._status


class Task(ABC):
    def __init__(self, account: dict):
        self._account = account
        self._parameters = None
        self._browser = None

    def connect(self) -> TaskAnswer:
        login = self._account.get('login') or ''
        password = self._account.get('password') or ''
        name = self._account.get("name") or ''
        auth = Authorizator()
        status, message = auth.authorizate(login=login, password=password, name=name)
        self._browser = auth.get_browser()
        if self._browser is None:
            self.complete()
        return TaskAnswer(message, status)

    def complete(self) -> None:
        self._browser.close()

    def is_ready_to_start(self) -> bool:
        return bool(self._browser)

    @abstractmethod
    def start(self):
        raise NotImplementedError("Данный метод нужно переопределить")

    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError("Данный метод нужно переопределить")


class TaskLike(Task):
    def __init__(self, account: dict):
        super().__init__(account)

    def get_name(self) -> str:
        return "Задача лайкинга"

    def start(self) -> TaskAnswer:
        """
        It likes users
        """
        self._parameters = get_parameters("like_collected_subscribers")
        return session_decorate(self.like_users)(self)

    @staticmethod
    def like_users(session: Session) -> (bool, str):
        return session.like_collected_users()


class TaskFilter(Task):
    AI_FILTER_TYPE = 0
    DEFAULT_FILTER_TYPE = 1

    def __init__(self, account: dict, filter_type: int):
        super().__init__(account)
        self._filter_type = filter_type

    def start(self) -> TaskAnswer:
        """
        It filters users depending on the type of filter
        """
        if self._filter_type == self.AI_FILTER_TYPE:
            self._parameters = get_parameters("ai_filter_subscribers")
            return session_decorate(self.filter_ai)(self)
        elif self._filter_type == self.DEFAULT_FILTER_TYPE:
            self._parameters = get_parameters("filter_subscribers")
            return session_decorate(self.filter_default)(self)
        else:
            return TaskAnswer(f"Тип {self._filter_type} для фильтрации подписчиков не определен")

    def get_name(self) -> str:
        if self._filter_type == self.AI_FILTER_TYPE:
            return "Задача фильтрации с помощью ИИ"
        elif self._filter_type == self.DEFAULT_FILTER_TYPE:
            return "Задача фильтрации с помощью настроенного фильтра"
        else:
            return "Задача неопределенной фильтрации"

    @staticmethod
    def filter_ai(session: Session) -> (bool, str):
        return session.filter_subscribers_with_ai()

    @staticmethod
    def filter_default(session: Session) -> (bool, str):
        return session.filter_subscribers()


class TaskCollection(Task):
    LAST_SUBSCRIBERS_TYPE = 0
    TOP_LIKERS_TYPE = 1

    def __init__(self, account: dict, collection_type: int):
        super().__init__(account)
        self._collection_type = collection_type

    def get_name(self) -> str:
        if self._collection_type == self.LAST_SUBSCRIBERS_TYPE:
            self._parameters = get_parameters("collect_subscribers")
            return "Задача сбора последних подписчиков"
        elif self._collection_type == self.TOP_LIKERS_TYPE:
            self._parameters = get_parameters("collect_likers")
            return "Задача сбора активных пользователей"
        else:
            return "Задача неопределенного сбора подписчиков"

    def start(self) -> TaskAnswer:
        """
        It collects users depending on the type of collection
        """
        if self._collection_type == self.LAST_SUBSCRIBERS_TYPE:
            return session_decorate(self.collect_last_subscribers)(self)
        elif self._collection_type == self.TOP_LIKERS_TYPE:
            return session_decorate(self.collect_top_likers)(self)
        else:
            return TaskAnswer(f"Тип {self._collection_type} для сбора подписчиков не определен")

    @staticmethod
    def collect_last_subscribers(session: Session) -> (bool, str):
        return session.collect_subscribers()

    @staticmethod
    def collect_top_likers(session: Session) -> (bool, str):
        return session.collect_active_users()


class TaskSequence:
    def __init__(self, tasks=None):
        self._tasks = [] if tasks is None else tasks

    def add_task(self, task: Task):
        self._tasks.append(task)

    def create_and_add_task(self, account: dict, task_name: str, task_type: int or None):
        if "collector" in task_name:
            task = TaskCollection(account, task_type)
        elif "filter" in task_name:
            task = TaskFilter(account, task_type)
        elif "liker" in task_name:
            task = TaskLike(account)
        else:
            return
        self.add_task(task)

    def run(self):
        for task in self._tasks:
            print(task.get_name())
            answer_connection = task.connect()
            print(answer_connection.get_message())
            if task.is_ready_to_start():
                answer_process = task.start()
                print(answer_process.get_message())
            task.complete()
