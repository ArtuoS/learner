from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from infra.adapters.postgres_adapter import PostgresAdapter
from infra.adapters.txt_extractor import TXTExtractor
from infra.database import ChromaDatabase
from infra.adapters.langchain_splitter import LangChainSplitter
from infra.adapters.repository.postgres.message_repository import PostgresMessageRepository
from infra.adapters.repository.postgres.user_repository import PostgresUserRepository
from infra.adapters.repository.postgres.file_repository import PostgresFileRepository
from infra.adapters.repository.postgres.session_repository import PostgresSessionRepository
from infra.adapters.openai_model import OpenAIModel
from infra.adapters.pdf_extractor import PDFExtractor
from infra.adapters.bcrypt_password_hasher import BcryptPasswordHasher
from infra.adapters.pyjwt_token_provider import PyJWTTokenProvider
from routes.router import router
from services.ask import AskService
from services.authentication import AuthenticationService
from services.extractor import ExtractorService
from services.file import FileService
from services.knowledge import KnowledgeService
from services.session import SessionService
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    db = ChromaDatabase()
    splitter = LangChainSplitter()
    pdf_extractor = PDFExtractor()
    txt_extractor = TXTExtractor()
    extractor_service = ExtractorService([pdf_extractor, txt_extractor])

    reranker = None
    if os.getenv("RERANKER_ENABLED", "false").lower() == "true":
        from infra.adapters.cross_encoder_reranker import CrossEncoderReranker
        reranker = CrossEncoderReranker()

    postgres = None
    message_repo = None
    user_repo = None
    file_repo = None
    session_repo = None
    if os.getenv("DATABASE_URL"):
        postgres = PostgresAdapter()
        message_repo = PostgresMessageRepository(postgres)
        user_repo = PostgresUserRepository(postgres)
        file_repo = PostgresFileRepository(postgres)
        session_repo = PostgresSessionRepository(postgres)

    password_hasher = BcryptPasswordHasher()
    token_provider = PyJWTTokenProvider()

    knowledge_service = KnowledgeService(db, splitter, reranker)

    model = OpenAIModel(knowledge_service)
    ask_service = AskService(model, message_repo)

    auth_service = AuthenticationService(user_repo, password_hasher, token_provider) if user_repo else None
    file_service = FileService(file_repo)
    session_service = SessionService(session_repo)

    app.state.knowledge_service = knowledge_service
    app.state.ask_service = ask_service
    app.state.extractor_service = extractor_service
    app.state.message_repo = message_repo
    app.state.user_repo = user_repo
    app.state.password_hasher = password_hasher
    app.state.token_provider = token_provider
    app.state.auth_service = auth_service
    app.state.file_service = file_service
    app.state.session_service = session_service
    app.state.sessions: dict[str, dict] = {}
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
