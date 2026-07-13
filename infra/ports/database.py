from abc import ABC, abstractmethod


class Database(ABC):

    @abstractmethod
    def execute(self, query: str, params: tuple = ()) -> list[dict]:
        pass
