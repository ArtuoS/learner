import chromadb
import os

class ChromaDatabase:
    collection: chromadb.Collection

    def __init__(self) -> None:
        client: chromadb.ClientAPI
        if os.getenv("LOCAL_DATABASE") == "false":
            client = chromadb.HttpClient(
                host=os.getenv("CHROMA_HOST", "localhost"),
                port=int(os.getenv("CHROMA_PORT", 8000)),
                database=os.getenv("CHROMA_DATABASE_NAME", "knowledge_db"),
                tenant=os.getenv("CHROMA_TENANT", "default_tenant")
            )
            print("ChromaDB client initialized with HTTP connection.")
        else:
            client = chromadb.PersistentClient(path="./chroma_db")

        self.collection = client.get_or_create_collection(name=os.getenv("CHROMA_COLLECTION_NAME", "knowledge"))
            