from uuid import UUID

from domain.repositories.session_repository import SessionRepository


class SessionService:

    def __init__(self, session_repo: SessionRepository | None = None) -> None:
        self.session_repo = session_repo

    def create(self, tenant_id: UUID) -> "Session":
        if self.session_repo is None:
            raise ValueError("Session repository is not available.")

        from domain.entities.session import Session

        session = Session(tenant_id=tenant_id)
        self.session_repo.save(session)
        return session

    def find_by_id(self, session_id: UUID) -> "Session | None":
        if self.session_repo is None:
            return None

        return self.session_repo.find_by_id(session_id)

    def list_by_tenant(self, tenant_id: UUID) -> list:
        if self.session_repo is None:
            return []

        return self.session_repo.list_by_tenant(tenant_id)
