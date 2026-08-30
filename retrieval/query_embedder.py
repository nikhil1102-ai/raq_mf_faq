import os
import logging
from dotenv import load_dotenv

load_dotenv()

_model = None


def _get_model():
    """
    Load the embedding model once (singleton).
    Tries ONNX backend first (2-5x faster on CPU), falls back to PyTorch.
    """
    global _model
    if _model is not None:
        return _model

    model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    logging.info(f"Loading embedding model: {model_name}")

    from sentence_transformers import SentenceTransformer

    # Try ONNX backend first — significantly faster on CPU
    try:
        _model = SentenceTransformer(model_name, backend="onnx")
        logging.info(f"Loaded '{model_name}' with ONNX backend (fast CPU inference)")
        return _model
    except Exception as e:
        logging.warning(f"ONNX backend unavailable ({e}), trying PyTorch backend")

    # Fallback to default PyTorch backend
    _model = SentenceTransformer(model_name)
    logging.info(f"Loaded '{model_name}' with PyTorch backend")
    return _model


def warm_up():
    """Pre-load the model so the first user query doesn't pay the loading cost."""
    _get_model()
    logging.info("Embedding model warmed up and ready.")


def embed_query(query: str) -> list[float]:
    model = _get_model()
    embedding = model.encode(query)
    return embedding.tolist()
