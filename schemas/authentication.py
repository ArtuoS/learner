
from pydantic import BaseModel


class LoginSchema(BaseModel):
    email: str
    password: str


class LoginOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterSchema(BaseModel):
    name: str
    email: str
    password: str


class RegisterOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"
