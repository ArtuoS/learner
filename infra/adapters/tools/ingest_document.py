from typing import Annotated

from langchain_core.tools import InjectedToolArg, tool
from services.knowledge import KnowledgeService

@tool
def ingest_document(url: str, service: Annotated[KnowledgeService, InjectedToolArg]) -> str:
    """
    Ingests a document from the specified file path and returns its content as a string.

    Args:
        url (str): The URL of the document to be ingested.
    """

    service.fetch_and_apply([url])
    return f"Document from {url} ingested successfully."