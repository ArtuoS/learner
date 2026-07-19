from uuid import UUID

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infra.ports.database import Database


class PostgresUserRepository(UserRepository):

    def __init__(self, db: Database) -> None:
        self.db = db

    def find_by_email(self, email: str) -> User | None:
        rows = self.db.execute(
            "SELECT id, name, email, password FROM users WHERE email = %s",
            (email,),
        )
        if not rows:
            return None
        row = rows[0]
        return User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            password=row["password"],
        )

    def find_by_id(self, user_id: UUID) -> User | None:
        rows = self.db.execute(
            "SELECT id, name, email, password FROM users WHERE id = %s",
            (str(user_id),),
        )
        if not rows:
            return None
        row = rows[0]
        return User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            password=row["password"],
        )
