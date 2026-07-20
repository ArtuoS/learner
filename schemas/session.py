from uuid import UUID

from pydantic import BaseModel


class SessionOutput(BaseModel):
    id: UUID
    tenant_id: UUID
