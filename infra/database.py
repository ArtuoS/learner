import chromadb
import os

class Database:
    collection: chromadb.Collection

    def __init__(self) -> None:
        client: chromadb.ClientAPI
        if os.getenv("LOCAL_DATABASE") == "false":
            client = chromadb.PersistentClient(path="./chroma_db")
        else:
            client = chromadb.EphemeralClient()

        self.collection = client.get_or_create_collection(name=os.getenv("CHROMA_COLLECTION_NAME", "knowledge"))