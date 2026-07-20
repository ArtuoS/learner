from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from services.ask import AskService
from services.knowledge import KnowledgeService

router = APIRouter()

WEB_TENANT_ID = uuid4()


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


def _sse_data(text: str) -> str:
    lines = text.split("\n")
    return "\n".join(f"data: {line}" for line in lines)


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@router.get("/", response_class=HTMLResponse)
async def get_index():
    html = Path(__file__).resolve().parent.parent / "web" / "index.html"
    return HTMLResponse(html.read_text())


@router.post("/chat", response_class=HTMLResponse)
async def post_chat(
    question: str = Form(...),
    request: Request = None,
):
    question = question.strip()
    if not question:
        return HTMLResponse("")

    session_id = str(uuid4())
    request.app.state.sessions[session_id] = {"question": question}

    html = _user_bubble(question)
    html += (
        f'<div id="sse-{session_id}">'
        f'  <div class="flex justify-start mb-4">'
        f'    <div class="bg-gray-700 rounded-2xl rounded-bl-sm px-4 py-2 max-w-lg"><span class="text-gray-400 italic">Thinking...</span></div>'
        f'  </div>'
        f'</div>'
        f'<script>'
        f'(function() {{'
        f'  var es = new EventSource("/chat/stream/{session_id}");'
        f'  var el = document.getElementById("sse-{session_id}");'
        f'  es.onmessage = function(e) {{ el.innerHTML = e.data; }};'
        f'  es.addEventListener("done", function() {{ es.close(); }});'
        f'}})();'
        f'</script>'
    )
    return HTMLResponse(html)


@router.get("/chat/stream/{session_id}")
async def chat_stream(
    session_id: str,
    request: Request,
    ask_service: AskService = Depends(_get_ask_service),
    knowledge_service: KnowledgeService = Depends(_get_knowledge_service),
):
    sessions = request.app.state.sessions
    session = sessions.pop(session_id, None)
    print(f"[chat_stream] session_id={session_id}, found={session is not None}")
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    question = session["question"]
    print(f"[chat_stream] question={question}")

    results = knowledge_service.query(question, WEB_TENANT_ID)
    print(f"[chat_stream] results count={len(results)}")
    if not results:
        async def no_context_stream():
            html = _assistant_bubble('No relevant context found.')
            yield _sse_data(html) + "\n\n"
            yield "event: done\ndata: \n\n"
        return StreamingResponse(no_context_stream(), media_type="text/event-stream")

    context = "\n\n".join(results)
    if len(context) > 3000:
        context = context[:3000] + "..."

    instructions = (
        "You are only allowed to answer questions about the context provided. "
        'If the question is not related to the context, respond with "I don\'t know.".'
    )

    async def event_stream():
        try:
            full_answer = ""
            async for token in ask_service.get_response_stream(instructions, context, question, WEB_TENANT_ID):
                full_answer += token
                print(f"[event_stream] Full Answer: {full_answer}. Token: {token}. Session {session_id}")
                html = _assistant_bubble(full_answer)
                yield _sse_data(html) + "\n\n"
            print(f"[event_stream] Stream completed for session {session_id}")
        except Exception as e:
            print(f"[event_stream] Error in stream: {e}")
            import traceback
            traceback.print_exc()
        finally:
            yield "event: done\ndata: \n\n"
            print(f"[event_stream] Done event sent for {session_id}")

    return StreamingResponse(event_stream(), media_type="text/event-stream")
