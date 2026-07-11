import tempfile

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status

from schemas.upload import UploadOutput
from services.knowledge import KnowledgeService

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def get_knowledge_service(request: Request) -> KnowledgeService:
    return request.app.state.knowledge_service


@router.post("/upload", response_model=UploadOutput, status_code=status.HTTP_200_OK)
async def upload_document(
    file: UploadFile,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
):
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if f".{ext}" not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if ext == "pdf":
        extractor = knowledge_service.pick_extractor(filename)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content_bytes)
            tmp_path = tmp.name
        try:
            text = extractor.extract(tmp_path)
        finally:
            import os
            os.unlink(tmp_path)
    else:
        text = content_bytes.decode("utf-8")

    chunks_inserted = knowledge_service.ingest_content(text)
    return UploadOutput(filename=filename, chunks_inserted=chunks_inserted)
