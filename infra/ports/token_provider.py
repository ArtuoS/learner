from abc import ABC, abstractmethod


class TokenProvider(ABC):

    @abstractmethod
    def create_token(self, payload: dict) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        pass
