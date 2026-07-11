from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from infra.adapters.txt_extractor import TXTExtractor
from infra.database import Database
from infra.adapters.langchain_splitter import LangChainSplitter
from infra.adapters.openai_model import OpenAIModel
from infra.adapters.pdf_extractor import PDFExtractor
from routes.router import router
from services.ask import AskService
from services.extractor import ExtractorService
from services.knowledge import KnowledgeService
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    db = Database()
    model = OpenAIModel()
    splitter = LangChainSplitter()
    pdf_extractor = PDFExtractor()
    txt_extractor = TXTExtractor()
    extractor_service = ExtractorService([pdf_extractor, txt_extractor])

    reranker = None
    if os.getenv("RERANKER_ENABLED", "false").lower() == "true":
        from infra.adapters.cross_encoder_reranker import CrossEncoderReranker
        reranker = CrossEncoderReranker()

    knowledge_service = KnowledgeService(db, splitter, extractor_service, reranker)
    ask_service = AskService(model)
    
    if os.getenv("FETCH", "false").lower() == "true":
        knowledge_service.fetch_and_apply([
            "https://raw.githubusercontent.com/NirDiamant/RAG_TECHNIQUES/main/data/Understanding_Climate_Change.pdf"
        ])
        
    app.state.knowledge_service = knowledge_service
    app.state.ask_service = ask_service
    app.state.extractor_service = extractor_service
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
