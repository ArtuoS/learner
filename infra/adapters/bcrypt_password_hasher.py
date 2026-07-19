from passlib.context import CryptContext

from infra.ports.password_hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):

    def __init__(self) -> None:
        self._context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self._context.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        return self._context.verify(password, hashed)
