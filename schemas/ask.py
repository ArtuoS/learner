from pydantic import BaseModel


class AskSchema(BaseModel):
    question: str
    session_id: str | None = None


class AskOutput(BaseModel):
    answer: str


class MessageOutput(BaseModel):
    from_field: str
    content: str
