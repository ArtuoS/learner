from fastapi import APIRouter

from routes.v1.ask import router as ask_router
from routes.v1.upload import router as upload_router
from routes.web import router as web_router

router = APIRouter()
router.include_router(ask_router, prefix="/v1", tags=["Ask"])
router.include_router(upload_router, prefix="/v1", tags=["Upload"])
router.include_router(web_router)