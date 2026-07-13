---
name: hexagonal-python
description: Build Python applications following Hexagonal (ports-and-adapters) architecture with FastAPI, Clean Architecture layering, and dependency injection via the app entry point.
license: MIT
compatibility: opencode
---

## What I do

Scaffold and maintain Python applications using Hexagonal Architecture (also called Ports & Adapters). The codebase at `@.` follows this pattern — use it as the reference.

## Project structure

```
<project>/
├── app.py                      # FastAPI entry point — wires dependencies via lifespan
├── pyproject.toml              # UV project config with dependencies
├── Makefile                    # dev commands: run, db, precommit
├── Dockerfile                  # multi-stage build with UV
├── docker-compose.yaml         # app + chromadb services
├── .env.example                # env template with defaults
├── .gitignore
├── infra/
│   ├── ports/                  # Abstract interfaces (ABCs)
│   │   ├── __init__.py
│   │   ├── model.py
│   │   ├── splitter.py
│   │   ├── reranker.py
│   │   └── extractor.py
│   ├── adapters/               # Concrete implementations
│   │   ├── __init__.py
│   │   ├── openai_model.py
│   │   ├── langchain_splitter.py
│   │   ├── cross_encoder_reranker.py
│   │   ├── pdf_extractor.py
│   │   └── txt_extractor.py
│   ├── database.py             # Infrastructure (chromadb client)
│   └── tools/                  # Reusable tools (langchain @tool decorated)
│       ├── __init__.py
│       └── answer_json.py
├── services/                   # Business logic — depends on ports, not adapters
│   ├── __init__.py
│   ├── ask.py
│   ├── knowledge.py
│   ├── extractor.py
│   └── formatter.py
├── routes/                     # HTTP layer (web + JSON API)
│   ├── __init__.py
│   ├── router.py               # Top-level APIRouter aggregation
│   ├── web.py                  # Form-based HTML endpoints (HTMX)
│   └── v1/                     # JSON API versioned routes
│       ├── __init__.py
│       ├── ask.py
│       └── upload.py
├── schemas/                    # Pydantic request/response models
│   ├── __init__.py
│   ├── ask.py
│   └── upload.py
└── web/                        # Static frontend assets
    └── index.html
```

## Key patterns

### 1. Ports (interfaces) in `infra/ports/`

Each port is an abstract base class (ABC) that defines the contract:

```python
from abc import ABC, abstractmethod

class Model(ABC):
    @abstractmethod
    def ask(self, instructions: str, context: str, question: str) -> str: ...
```

### 2. Adapters (implementations) in `infra/adapters/`

Each adapter implements a port concretely and is swappable:

```python
from infra.ports.model import Model

class OpenAIModel(Model):
    def ask(self, instructions: str, context: str, question: str) -> str:
        # actual OpenAI call
```

### 3. Business logic in `services/`

Services depend on ports (abstractions), never on concrete adapters. Injected via constructor:

```python
class AskService:
    def __init__(self, model: Model) -> None:  # depends on port, not adapter
        self.model = model

    def get_response(self, instructions: str, context: str, question: str) -> str:
        return self.model.ask(instructions, context, question)
```

### 4. Wiring in `app.py`

Dependencies are assembled at the entry point via the FastAPI `lifespan` context manager. All concrete adapters are instantiated here and injected into services:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database()
    model = OpenAIModel()
    splitter = LangChainSplitter()
    pdf_extractor = PDFExtractor()
    txt_extractor = TXTExtractor()
    extractor_service = ExtractorService([pdf_extractor, txt_extractor])

    # Optional — imported only when enabled to keep startup fast
    reranker = None
    if os.getenv("RERANKER_ENABLED", "false").lower() == "true":
        from infra.adapters.cross_encoder_reranker import CrossEncoderReranker
        reranker = CrossEncoderReranker()

    knowledge_service = KnowledgeService(db, splitter, extractor_service, reranker)
    ask_service = AskService(model)

    app.state.knowledge_service = knowledge_service
    app.state.ask_service = ask_service
    yield
```

### 5. Dependency injection in routes

Routes access services through FastAPI `Depends()` and `request.app.state`:

```python
def get_knowledge_service(request: Request) -> KnowledgeService:
    return request.app.state.knowledge_service

@router.post("/ask", response_model=AskOutput)
def ask_question(
    ask_input: AskSchema,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
): ...
```

## Conventions

- **No circular imports** — `infra/` never imports from `services/` or `routes/`. `services/` never imports from `routes/`.
- **One service per responsibility** — `KnowledgeService` handles ingestion + retrieval, `AskService` handles LLM calls, `ExtractorService` handles file extraction.
- **Configuration via environment** — All configurable values come from environment variables with sensible defaults. See `.env.example`.
- **Lazy imports for heavy deps** — Large libraries (sentence-transformers, etc.) are imported inside conditionals, not at module level, to keep startup fast.
- **Tools are @tool decorated** — LangChain tools go in `infra/tools/` and are bound to the model via `.bind_tools()`.

## When to use me

Use this skill when:
- Starting a new Python project and you want a clean, maintainable architecture
- You need to add a new port (interface) and its adapter(s)
- You need to add a new service with business logic
- You need to add a new HTTP route following the existing patterns
- You need to add a new tool for function calling

I will follow the exact same conventions, naming, and layering as the reference codebase.
