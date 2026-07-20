from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from domain.entities.user import User
from routes.dependencies import get_current_user
from schemas.ask import MessageOutput
from schemas.session import SessionOutput
from services.ask import AskService
from services.session import SessionService

router = APIRouter()


def get_session_service(request: Request) -> SessionService:
    return request.app.state.session_service


def get_ask_service(request: Request) -> AskService:
    return request.app.state.ask_service


@router.post("/sessions", response_model=SessionOutput, status_code=status.HTTP_201_CREATED)
def create_session(
    user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    session = session_service.create(user.id)
    return SessionOutput(id=session.id, tenant_id=session.tenant_id)


@router.get("/sessions", response_model=list[SessionOutput], status_code=status.HTTP_200_OK)
def list_sessions(
    user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
):
    sessions = session_service.list_by_tenant(user.id)
    return [SessionOutput(id=s.id, tenant_id=s.tenant_id) for s in sessions]


@router.get("/sessions/{session_id}/messages", response_model=list[MessageOutput], status_code=status.HTTP_200_OK)
def list_session_messages(
    session_id: str,
    user: User = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service),
    ask_service: AskService = Depends(get_ask_service),
):
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session_id format.")

    session = session_service.find_by_id(session_uuid)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    if session.tenant_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this session.")

    messages = ask_service.list_session_messages(session_uuid, user.id)
    return [MessageOutput(from_field=m.from_field, content=m.content) for m in messages]
