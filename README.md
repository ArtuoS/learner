# Learner

A RAG (Retrieval-Augmented Generation) chatbot that ingests documents, stores them as vector embeddings, and answers questions by retrieving relevant context.

## Features

- **Document ingestion** - Upload PDF/TXT files or fetch from URLs
- **Semantic search** - ChromaDB vector similarity retrieval
- **Cross-encoder reranking** - Optional reranking for higher accuracy responses
- **Web UI** - Chat interface built with HTMX and Tailwind CSS
- **REST API** - JSON endpoints for programmatic access
- **Docker support** - Containerized deployment with ChromaDB

## Architecture

The project follows Clean Architecture with ports and adapters:

```
app.py                          FastAPI entry point
routes/                         HTTP handlers (web + JSON API)
schemas/                        Pydantic request/response models
services/                       Business logic
  ask.py                        LLM response generation
  knowledge.py                  Document ingestion and retrieval
infra/
  database.py                   ChromaDB client setup
  ports/                        Abstract interfaces (Model, Reranker, Splitter, Extractor)
  adapters/                     Concrete implementations
```

## Setup

### 1. Clone and install

```bash
git clone <repo-url>
cd learner
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your settings. The only required variable is `OPENAI_API_KEY`.

### 3. Run

**Local (two terminals):**
```bash
make db      # starts ChromaDB on port 8000
make run     # starts the app on port 8001
```

**Docker:**
```bash
docker compose up --build
```

The app will be available at `http://localhost:8001`.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | - | Required. Your OpenAI API key |
| `OPENAI_MODEL_NAME` | `gpt-4o-mini` | OpenAI model to use |
| `LOCAL_DATABASE` | `false` | Use local persistent ChromaDB |
| `CHROMA_HOST` | `localhost` | ChromaDB host (`chromadb` in Docker) |
| `CHROMA_PORT` | `8000` | ChromaDB port |
| `FETCH` | `false` | Auto-fetch sample PDF on startup |

### Reranker

Optional cross-encoder reranking improves response accuracy by retrieving more candidates and re-scoring them for relevance.

| Variable | Default | Description |
|---|---|---|
| `RERANKER_ENABLED` | `false` | Enable reranking |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder model |
| `RERANKER_INITIAL_RESULTS` | `10` | Candidates fetched from ChromaDB |
| `RERANKER_FINAL_RESULTS` | `3` | Results returned after reranking |

## API

### `POST /v1/ask`

```json
// Request
{ "question": "What is climate change?" }

// Response
{ "answer": "Climate change refers to..." }
```

### `POST /chat`

Form endpoint for the web UI. Returns HTML chat bubbles.

### `POST /v1/upload`

Upload PDF or TXT files to ingest into the knowledge base.

## Stack

- **FastAPI** - Web framework
- **ChromaDB** - Vector database
- **OpenAI** - LLM provider
- **LangChain** - Text splitting
- **sentence-transformers** - Cross-encoder reranking (optional)
- **HTMX + Tailwind CSS** - Frontend
