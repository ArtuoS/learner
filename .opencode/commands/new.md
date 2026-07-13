---
description: Scaffold a new hexagonal architecture Python project
agent: build
---

You are building a new Python project called "$ARGUMENTS" following Hexagonal Architecture (Ports & Adapters).

The reference codebase at `@.` shows the exact patterns to follow. Here is the structure to create:

```
<project>/
├── app.py                      # FastAPI entry point with lifespan DI
├── pyproject.toml              # UV project config
├── Makefile                    # dev commands
├── Dockerfile                  # multi-stage build with UV
├── docker-compose.yaml         # app + chromadb services
├── .env.example                # env template
├── .gitignore
├── infra/
│   ├── __init__.py
│   ├── ports/                  # Abstract ABC interfaces
│   │   ├── __init__.py
│   │   └── model.py
│   ├── adapters/               # Concrete implementations
│   │   ├── __init__.py
│   │   └── openai_model.py
│   └── database.py
├── services/                   # Business logic
│   ├── __init__.py
│   └── example.py
├── routes/                     # HTTP handlers
│   ├── __init__.py
│   ├── router.py
│   ├── web.py
│   └── v1/
│       ├── __init__.py
│       └── example.py
└── schemas/                    # Pydantic models
    ├── __init__.py
    └── example.py
```

## Requirements

1. **ports/model.py** — Abstract `Model` class with `ask(instructions, context, question) -> str`
2. **adapters/openai_model.py** — `OpenAIModel` implementing `Model` using `langchain_openai.ChatOpenAI`
3. **app.py** — FastAPI app with `lifespan` that wires dependencies into `app.state`
4. **routes/** — Use `APIRouter`, wire up with `Depends()` using `request.app.state`
5. **pyproject.toml** — Dependencies: `fastapi`, `uvicorn[standard]`, `openai`, `python-dotenv`, `langchain-openai`, `chromadb`, `pypdf`, `python-multipart`, `tiktoken`
6. **Dockerfile** — Use `python:3.13-slim`, copy uv from `ghcr.io/astral-sh/uv:latest`
7. **docker-compose.yaml** — Two services: `chromadb` and `app`
8. **Startup must be fast** — No heavy imports at module level. Use lazy imports inside lifespan conditionals.

Follow the exact conventions from the reference:
- `infra/` never imports from `services/` or `routes/`
- `services/` never imports from `routes/`
- All config via env vars with defaults in `.env.example`
- Constructor injection for all services
- Routes access services via `request.app.state` + `Depends()`
