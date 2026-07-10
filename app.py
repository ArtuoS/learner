from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from infra.adapters.langchain_splitter import LangChainSplitter
from infra.adapters.openai_model import OpenAIModel
from infra.database import Database
from routes.router import router
from services.ask import AskService
from services.knowledge import KnowledgeService


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    db = Database()
    model = OpenAIModel()
    splitter = LangChainSplitter()
    knowledge_service = KnowledgeService(db, splitter)
    ask_service = AskService(model)
    knowledge_service.fetch_and_apply(
        [
            "https://raw.githubusercontent.com/gastonstat/StarWars/refs/heads/master/Text_files/EpisodeIV_dialogues.txt"
        ]
    )
    app.state.knowledge_service = knowledge_service
    app.state.ask_service = ask_service
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
