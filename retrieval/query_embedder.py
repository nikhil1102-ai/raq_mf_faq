import os
import logging
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

_model = None

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        logging.info(f"Loading embedding model: {model_name}")
        _model = SentenceTransformer(model_name)
    return _model

def embed_query(query: str) -> list[float]:
    model = _get_model()
    embedding = model.encode(query)
    return embedding.tolist()
