
from domain.repositories.user_repository import UserRepository
from infra.ports.password_hasher import PasswordHasher
from infra.ports.token_provider import TokenProvider
from domain.entities.user import User

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

    def register(self, name: str, email: str, password: str) -> str:
        existing = self.user_repo.find_by_email(email)
        if existing is not None:
            raise ValueError("Email is already registered.")

        hashed = self.password_hasher.hash_password(password)
        user = User(name=name, email=email, password=hashed)
        self.user_repo.save(user)

        token = self.token_provider.create_token({"sub": str(user.id), "name": user.name})
        return token
