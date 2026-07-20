from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Session:
    tenant_id: UUID
    id: UUID = field(default_factory=uuid4)
