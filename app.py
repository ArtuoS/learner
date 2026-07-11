from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from infra.database import Database
from infra.adapters.langchain_splitter import LangChainSplitter
from infra.adapters.openai_model import OpenAIModel
from infra.adapters.pdf_extractor import PDFExtractor
from routes.router import router
from services.ask import AskService
from services.knowledge import KnowledgeService
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    db = Database()
    model = OpenAIModel()
    splitter = LangChainSplitter()
    pdf_extractor = PDFExtractor(".pdf")
    knowledge_service = KnowledgeService(db, splitter, [pdf_extractor])
    ask_service = AskService(model)
    
    if os.getenv("FETCH", "false").lower() == "true":
        knowledge_service.fetch_and_apply([
            "https://raw.githubusercontent.com/NirDiamant/RAG_TECHNIQUES/main/data/Understanding_Climate_Change.pdf"
        ])
        
    app.state.knowledge_service = knowledge_service
    app.state.ask_service = ask_service
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
