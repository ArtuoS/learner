import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from domain.entities.user import User
from routes.dependencies import get_current_user
from schemas.ask import AskOutput, AskSchema
from services.ask import AskService
from services.knowledge import KnowledgeService
from services.session import SessionService

router = APIRouter()


def get_ask_service(request: Request) -> AskService:
    return request.app.state.ask_service


def get_knowledge_service(request: Request) -> KnowledgeService:
    return request.app.state.knowledge_service


def get_session_service(request: Request) -> SessionService:
    return request.app.state.session_service


def _validate_session(session_id: str, user: User, session_service: SessionService) -> UUID:
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session_id format.")

    session = session_service.find_by_id(session_uuid)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    if session.tenant_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this session.")

    return session_uuid


@router.post("/ask", response_model=AskOutput, status_code=status.HTTP_200_OK)
def ask_question(
    ask_input: AskSchema,
    user: User = Depends(get_current_user),
    ask_service: AskService = Depends(get_ask_service),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    session_service: SessionService = Depends(get_session_service),
):
    if not ask_input.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if not ask_input.session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    session_uuid = _validate_session(ask_input.session_id, user, session_service)

    results = knowledge_service.query(ask_input.question, user.id)
    if not results:
        raise HTTPException(status_code=404, detail="No relevant context found.")

    context = "\n\n".join(results)
    if len(context) > 3000:
        context = context[:3000] + "..."

    answer = ask_service.get_response(
        "You are only allowed to answer questions about the context provided. "
        'If the question is not related to the context, respond with "I don\'t know.".',
        context,
        ask_input.question,
        user.id,
        session_uuid,
    )
    return AskOutput(answer=answer)


@router.post("/ask/stream", status_code=status.HTTP_200_OK)
async def ask_stream(
    ask_input: AskSchema,
    user: User = Depends(get_current_user),
    ask_service: AskService = Depends(get_ask_service),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    session_service: SessionService = Depends(get_session_service),
):
    if not ask_input.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if not ask_input.session_id:
        raise HTTPException(status_code=400, detail="session_id is required.")

    session_uuid = _validate_session(ask_input.session_id, user, session_service)

    results = knowledge_service.query(ask_input.question, user.id)
    if not results:
        raise HTTPException(status_code=404, detail="No relevant context found.")

    context = "\n\n".join(results)
    if len(context) > 3000:
        context = context[:3000] + "..."

    instructions = (
        "You are only allowed to answer questions about the context provided. "
        'If the question is not related to the context, respond with "I don\'t know.".'
    )

    async def event_stream():
        async for token in ask_service.get_response_stream(instructions, context, ask_input.question, user.id, session_uuid):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
