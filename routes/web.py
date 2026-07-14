import json
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from services.ask import AskService
from services.knowledge import KnowledgeService

router = APIRouter()


def _get_ask_service(request: Request) -> AskService:
    return request.app.state.ask_service


def _get_knowledge_service(request: Request) -> KnowledgeService:
    return request.app.state.knowledge_service


def _user_bubble(text: str) -> str:
    text = _escape(text)
    return f'<div class="flex justify-end mb-4"><div class="bg-blue-600 rounded-2xl rounded-br-sm px-4 py-2 max-w-lg">{text}</div></div>'


def _assistant_bubble(text: str) -> str:
    text = _escape(text)
    return f'<div class="flex justify-start mb-4"><div class="bg-gray-700 rounded-2xl rounded-bl-sm px-4 py-2 max-w-lg">{text}</div></div>'


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@router.get("/", response_class=HTMLResponse)
async def get_index():
    html = Path(__file__).resolve().parent.parent / "web" / "index.html"
    return HTMLResponse(html.read_text())


@router.post("/chat", response_class=HTMLResponse)
async def post_chat(
    question: str = Form(...),
    knowledge_service: KnowledgeService = Depends(_get_knowledge_service),
):
    question = question.strip()
    if not question:
        return HTMLResponse("")

    results = knowledge_service.query(question)
    if not results:
        return HTMLResponse(
            _user_bubble(question) + _assistant_bubble("No relevant context found.")
        )

    context = "\n\n".join(results)
    if len(context) > 3000:
        context = context[:3000] + "..."

    encoded_question = quote(question)
    encoded_context = quote(context)

    html = _user_bubble(question)
    html += (
        f'<div hx-ext="sse" sse-connect="/chat/stream?question={encoded_question}&context={encoded_context}"'
        f' sse-swap="message" sse-close="done">'
        f'  <div class="flex justify-start mb-4">'
        f'    <div class="bg-gray-700 rounded-2xl rounded-bl-sm px-4 py-2 max-w-lg"><span class="text-gray-400 italic">Thinking...</span></div>'
        f'  </div>'
        f"</div>"
    )
    return HTMLResponse(html)


@router.get("/chat/stream")
async def chat_stream(
    question: str = Query(...),
    context: str = Query(...),
    ask_service: AskService = Depends(_get_ask_service),
):
    instructions = (
        "You are only allowed to answer questions about the context provided. "
        'If the question is not related to the context, respond with "I don\'t know.".'
    )

    async def event_stream():
        full_answer = ""
        async for token in ask_service.get_response_stream(instructions, context, question):
            full_answer += token
            yield f"data: {_assistant_bubble(full_answer)}\n\n"
        yield "event: done\ndata: \n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
