from uuid import UUID

from domain.repositories.user_repository import UserRepository
from infra.ports.password_hasher import PasswordHasher
from infra.ports.token_provider import TokenProvider


class AuthenticationService:

    def __init__(
        self,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
        token_provider: TokenProvider,
    ) -> None:
        self.user_repo = user_repo
        self.password_hasher = password_hasher
        self.token_provider = token_provider

    def login(self, email: str, password: str) -> str:
        user = self.user_repo.find_by_email(email)
        if user is None:
            raise ValueError("Invalid email or password.")

        if not self.password_hasher.verify_password(password, user.password):
            raise ValueError("Invalid email or password.")

        token = self.token_provider.create_token({"sub": str(user.id), "name": user.name})
        return token
