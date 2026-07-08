from pydantic import BaseModel


class AskSchema(BaseModel):
    question: str


class AskOutput(BaseModel):
    answer: str
