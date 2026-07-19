from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infra.ports.token_provider import TokenProvider
from uuid import UUID

security = HTTPBearer()


def get_user_repository(request: Request) -> UserRepository:
    return request.app.state.user_repo


def get_token_provider(request: Request) -> TokenProvider:
    return request.app.state.token_provider


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository),
    token_provider: TokenProvider = Depends(get_token_provider),
) -> User:
    token = credentials.credentials
    try:
        payload = token_provider.decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    user = user_repo.find_by_id(user_uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    return user
