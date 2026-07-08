from fastapi import APIRouter

from routes.v1.ask import router as ask_router

router = APIRouter()
router.include_router(ask_router, prefix="/v1", tags=["Ask"])