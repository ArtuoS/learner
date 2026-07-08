from fastapi import APIRouter, Depends, HTTPException, Request, status

from schemas.ask import AskOutput, AskSchema
from services.ask import AskService
from services.knowledge import KnowledgeService

router = APIRouter()


def get_ask_service(request: Request) -> AskService:
    return request.app.state.ask_service


def get_knowledge_service(request: Request) -> KnowledgeService:
    return request.app.state.knowledge_service


@router.post("/ask", response_model=AskOutput, status_code=status.HTTP_200_OK)
def ask_question(
    ask_input: AskSchema,
    ask_service: AskService = Depends(get_ask_service),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
):
    if not ask_input.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    results = knowledge_service.query(ask_input.question)
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
    )
    return AskOutput(answer=answer)
