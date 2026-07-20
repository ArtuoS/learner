from typing import Annotated

from langchain_core.tools import InjectedToolArg, tool
from services.knowledge import KnowledgeService

@tool
def ingest_document(url: str, service: Annotated[KnowledgeService, InjectedToolArg]) -> str:
    """
    Ingests a document from the specified URL and returns its content as a string.

    Args:
        url (str): The URL of the document to be ingested.
    """
    raise NotImplementedError("Document ingestion via tool is not supported. Use the /upload endpoint instead.")