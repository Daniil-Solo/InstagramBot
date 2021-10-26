from abc import ABC, abstractmethod

from Authorizator import Authorizator
from Session import Session


class TaskAnswer:
    def __init__(self, message, status=None, data=None):
        self._message = message
        self._status = status
        self._data = data

    def get_message(self) -> str:
        return self._message

    def get_status(self) -> bool:
        return self._status

    def get_data(self) -> list:
        return self._data


class Task(ABC):
    def __init__(self, account):
        self._account = account
        self._browser = None

    def connect(self) -> TaskAnswer:
        login = self._account.get('login') or ''
        password = self._account.get('password') or ''
        auth = Authorizator()
        status, message = auth.authorizate(login=login, password=password)
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


class TaskCollection(Task):
    LAST_SUBSCRIBERS_TYPE = 0
    TOP_LIKERS_TYPE = 1

    def __init__(self, account, master_name, collection_type, parameters, idm):
        super().__init__(account)
        self._master_name = master_name
        self._collection_type = collection_type
        self._parameters = parameters
        self._idm = idm

    def start(self) -> TaskAnswer:
        """
        It collects users depending on the type of collection
        """
        if self._collection_type == TaskCollection.LAST_SUBSCRIBERS_TYPE:
            return session_decorate(self.collect_last_subscribers)(self)
        elif self._collection_type == TaskCollection.TOP_LIKERS_TYPE:
            return session_decorate(self.collect_top_likers)(self)
        else:
            return TaskAnswer(f"Тип {self._collection_type} для сбора подписчиков не определен")

    @staticmethod
    def collect_last_subscribers(session: Session) -> (bool, str):
        return session.generate_subscribers()

    @staticmethod
    def collect_top_likers(session: Session) -> (bool, str):
        return session.collect_active_users()


def session_decorate(session_function):
    def wrapped(self):
        session = Session(parameters=self._parameters, browser=self._browser, idm=self._idm)
        status, msg = session_function(session)
        users = session.get_users()
        return TaskAnswer(message=msg, status=status, data=users)
    return wrapped
