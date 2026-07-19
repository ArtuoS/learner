import os
from datetime import datetime, timedelta, timezone

import jwt

from infra.ports.token_provider import TokenProvider


class PyJWTTokenProvider(TokenProvider):

    def __init__(self) -> None:
        self._secret_key = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
        self._algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self._expiration_minutes = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))

    def create_token(self, payload: dict) -> str:
        to_encode = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._expiration_minutes)
        to_encode["exp"] = expire
        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
