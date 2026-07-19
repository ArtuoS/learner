from uuid import UUID

from pydantic import BaseModel


class LoginSchema(BaseModel):
    email: str
    password: str


class LoginOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"
