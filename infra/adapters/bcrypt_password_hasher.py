import hashlib

import bcrypt

from infra.ports.password_hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    
    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(
            self._prehash(password).encode(), bcrypt.gensalt()
        ).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(
            self._prehash(password).encode(), hashed.encode()
        )

    def _prehash(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()