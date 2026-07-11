from pydantic import BaseModel


class UploadOutput(BaseModel):
    filename: str
    chunks_inserted: int
