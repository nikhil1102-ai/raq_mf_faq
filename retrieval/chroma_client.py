import os
import chromadb
from dotenv import load_dotenv

load_dotenv()

def get_chroma_client():
    persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
    client = chromadb.PersistentClient(path=persist_directory)
    return client

def get_collection():
    client = get_chroma_client()
    collection_name = os.getenv("COLLECTION_NAME", "mf_faq_corpus")
    collection = client.get_or_create_collection(name=collection_name)
    return collection

if __name__ == "__main__":
    col = get_collection()
    print(f"Collection '{col.name}' initialized successfully.")
