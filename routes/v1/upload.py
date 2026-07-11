import tempfile
import os

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status

from schemas.upload import UploadOutput
from services.extractor import ExtractorService
from services.knowledge import KnowledgeService

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def get_knowledge_service(request: Request) -> KnowledgeService:
    return request.app.state.knowledge_service


def get_extractor_service(request: Request) -> ExtractorService:
    return request.app.state.extractor_service


@router.post("/upload", response_model=UploadOutput, status_code=status.HTTP_200_OK)
async def upload_document(
    file: UploadFile,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    extractor_service: ExtractorService = Depends(get_extractor_service),
):
    filename = file.filename or ""
    if not _is_allowed_file(filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    suffix = f".{filename.lower().rsplit('.', 1)[-1]}"
    text: str = ""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content_bytes)
        tmp_path = tmp.name
    try:
        text = extractor_service.extract(tmp_path)
    finally:
        os.unlink(tmp_path)

    chunks_inserted = knowledge_service.ingest_content(text)
    return UploadOutput(filename=filename, chunks_inserted=chunks_inserted)


def _is_allowed_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
