from uuid import UUID

from domain.entities.session import Session
from domain.repositories.session_repository import SessionRepository
from infra.ports.database import Database


class PostgresSessionRepository(SessionRepository):

    def __init__(self, db: Database) -> None:
        self.db = db

    def save(self, session: Session) -> None:
        self.db.execute(
            "INSERT INTO sessions (id, tenant_id) VALUES (%s, %s)",
            (str(session.id), str(session.tenant_id)),
        )

    def find_by_id(self, session_id: UUID) -> Session | None:
        rows = self.db.execute(
            "SELECT id, tenant_id FROM sessions WHERE id = %s",
            (str(session_id),),
        )
        if not rows:
            return None
        row = rows[0]
        return Session(id=row["id"], tenant_id=row["tenant_id"])

    def list_by_tenant(self, tenant_id: UUID) -> list[Session]:
        rows = self.db.execute(
            "SELECT id, tenant_id FROM sessions WHERE tenant_id = %s ORDER BY id DESC",
            (str(tenant_id),),
        )
        return [Session(id=row["id"], tenant_id=row["tenant_id"]) for row in rows]
