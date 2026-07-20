# Learner

A multi-tenant RAG (Retrieval-Augmented Generation) chatbot with per-user document isolation, optional cross-encoder reranking, and real-time streaming responses.

## How It Works

### RAG Pipeline

```
Upload                          Query
  │                               │
  ▼                               ▼
File (PDF/TXT)              User question
  │                               │
  ▼                               ▼
Text Extraction              ChromaDB vector search
(pypdf / open)              (filtered by tenant_id)
  │                               │
  ▼                               ▼
Chunking                     Candidate chunks
(RecursiveCharacterTextSplitter)    │
 500 tokens, 50 overlap           ▼
  │                          [Optional] Cross-encoder reranking
  ▼                          (ms-marco-MiniLM-L-6-v2)
ChromaDB insert                    │
(+ tenant_id metadata)            ▼
                          Top 3 relevant chunks
                                    │
                                    ▼
                          LLM prompt (context + question)
                                    │
                                    ▼
                          Streaming response to user
```

### Document Ingestion

1. User uploads a PDF or TXT file (via web UI or API)
2. Text is extracted using `pypdf` (PDF) or direct read (TXT)
3. Content is split into **500-token chunks** with **50-token overlap** using LangChain's `RecursiveCharacterTextSplitter` with `tiktoken` (`o200k_base` encoding)
4. Each chunk is stored in ChromaDB with a `tenant_id` metadata tag and a deterministic MD5-based ID

### Retrieval

1. User asks a question
2. ChromaDB performs semantic similarity search, filtered by the user's `tenant_id` -- **only the user's own documents are searched**
3. Without reranking: top 3 results are returned directly
4. With reranking: 10 candidates are fetched, scored by a cross-encoder, and the top 3 are returned
5. Retrieved chunks are assembled into a context block (max 3000 chars) and sent to the LLM with a system prompt restricting answers to the provided context

### Multi-Tenancy

Every document chunk in ChromaDB carries a `tenant_id` metadata field matching the uploading user's UUID. Queries include a `where={"tenant_id": "..."}` filter, ensuring **users can only retrieve their own uploaded documents**. This is enforced at the ChromaDB query level, not just the application layer.

Authentication is JWT-based (HS256, 30-minute expiry). The web UI uses a shared anonymous tenant ID.

### Reranking

When `RERANKER_ENABLED=true`, the pipeline fetches more candidates from ChromaDB (default 10) and passes them through a **cross-encoder** (`cross-encoder/ms-marco-MiniLM-L-6-v2`) that scores each (query, document) pair for relevance. Only the top-scoring results (default 3) are sent to the LLM.

This improves accuracy over pure vector similarity because cross-encoders see the full query-document pair rather than independent embeddings.

| Variable | Default | Description |
|---|---|---|
| `RERANKER_ENABLED` | `false` | Enable reranking |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder model |
| `RERANKER_INITIAL_RESULTS` | `10` | Candidates fetched from ChromaDB |
| `RERANKER_FINAL_RESULTS` | `3` | Results returned after reranking |

## Tech Stack

| Layer | Technology |
|---|---|
| Web Framework | FastAPI |
| ASGI Server | Uvicorn |
| Vector Database | ChromaDB |
| LLM Provider | OpenAI (GPT-4o-mini) |
| Text Splitting | LangChain `RecursiveCharacterTextSplitter` |
| Token Counting | tiktoken (`o200k_base`) |
| PDF Parsing | pypdf |
| Reranking | sentence-transformers (`CrossEncoder`) |
| Relational DB | PostgreSQL 16 (optional) |
| Password Hashing | bcrypt (SHA-256 pre-hash) |
| JWT Auth | PyJWT (HS256) |
| Frontend | Vanilla JS + Tailwind CSS |
| Python | 3.13 |
| Linting | Ruff |

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` -- the only required variable is `OPENAI_API_KEY`.

### 3. Start ChromaDB and the app

```bash
# Terminal 1: ChromaDB
make db

# Terminal 2: App (http://localhost:8001)
make run
```

### 4. (Optional) Start PostgreSQL

For user authentication, chat history persistence, and file tracking:

```bash
docker compose up postgres
```

Without PostgreSQL, the app runs in anonymous mode with no auth and no session history.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | *(required)* | OpenAI API key |
| `OPENAI_MODEL_NAME` | `gpt-4o-mini` | LLM model |
| `LOCAL_DATABASE` | `false` | Use local persistent ChromaDB (`./chroma_db`) |
| `CHROMA_HOST` | `localhost` | ChromaDB host |
| `CHROMA_PORT` | `8000` | ChromaDB port |
| `CHROMA_DATABASE_NAME` | `knowledge_db` | ChromaDB database |
| `CHROMA_COLLECTION_NAME` | `knowledge` | ChromaDB collection |
| `DATABASE_URL` | *(empty = disabled)* | PostgreSQL connection string |
| `JWT_SECRET_KEY` | `change-me-in-production` | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_EXPIRATION_MINUTES` | `30` | Token lifetime |

## API Endpoints

### Authentication

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/authentication/register` | Create account `{ name, email, password }` |
| `POST` | `/v1/authentication/login` | Sign in `{ email, password }` |

### Sessions

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/sessions` | Create a new chat session |
| `GET` | `/v1/sessions` | List all sessions for the user |
| `GET` | `/v1/sessions/{id}/messages` | Get message history for a session |

### RAG

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/ask` | Ask a question `{ question, session_id }` |
| `POST` | `/v1/ask/stream` | Ask with SSE streaming `{ question, session_id }` |

### Upload

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/upload` | Upload PDF/TXT file (multipart form) |

### Web UI

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Single-page app with login, sessions, and chat |

## Architecture

The project follows **Hexagonal Architecture** (ports and adapters):

```
app.py                          FastAPI entry point + DI wiring
routes/
  v1/                           JSON API (auth, sessions, ask, upload)
  web.py                        Web UI routes
domain/
  entities/                     User, Session, Message, File
  repositories/                 Repository interfaces
services/                       Business logic
  knowledge.py                  Ingestion, chunking, storage, retrieval
  ask.py                        LLM interaction + message persistence
  authentication.py             Login/register with JWT
  session.py                    Session CRUD
  extractor.py                  Text extraction dispatch
infra/
  database.py                   ChromaDB client setup
  ports/                        Abstract interfaces
    model.py                    LLM port
    splitter.py                 Text splitting port
    reranker.py                 Reranking port
    extractor.py                Text extraction port
    database.py                 SQL database port
    password_hasher.py          Hashing port
    token_provider.py           JWT port
  adapters/                     Concrete implementations
    openai_model.py             OpenAI via LangChain
    langchain_splitter.py       RecursiveCharacterTextSplitter
    cross_encoder_reranker.py   sentence-transformers CrossEncoder
    pdf_extractor.py            pypdf
    txt_extractor.py            Direct file read
    postgres_adapter.py         psycopg2 + auto-migration
    bcrypt_password_hasher.py   bcrypt + SHA-256
    pyjwt_token_provider.py     PyJWT
    repository/postgres/        Repository implementations
```

All adapters are behind port interfaces, making it straightforward to swap implementations (e.g., replace OpenAI with a local LLM, or ChromaDB with another vector store).

## Web UI

The SPA at `http://localhost:8001` provides:

- **Login / Register** screens for user authentication
- **Sessions** screen with an **Upload** button (PDF/TXT) and **+ New Chat** button
- **Chat** screen with real-time streaming responses via SSE
