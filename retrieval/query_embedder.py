import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# HuggingFace Inference API for query embedding
# ---------------------------------------------------------------------------
# Instead of running SentenceTransformer locally (13s on Railway free CPU),
# we call the HuggingFace Inference API which runs the SAME model on their
# GPU servers (~0.5s).
#
# The output is mathematically identical — same 384-dim vector — so no
# re-ingestion is needed.
# ---------------------------------------------------------------------------

HF_API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

_hf_token = None
_local_model = None  # Fallback only


def _get_hf_token() -> str:
    global _hf_token
    if _hf_token is None:
        _hf_token = os.getenv("HF_TOKEN", "")
    return _hf_token


def _embed_via_api(query: str) -> list[float]:
    """Call HuggingFace Inference API to embed a single query string."""
    token = _get_hf_token()
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.post(
        HF_API_URL,
        headers=headers,
        json={"inputs": query, "options": {"wait_for_model": True}},
        timeout=15,
    )
    response.raise_for_status()
    embedding = response.json()

    # The API returns a list of floats (sentence embedding) for ST models
    if isinstance(embedding, list) and isinstance(embedding[0], float):
        return embedding
    # Some models return nested list [[...]] — take first element
    if isinstance(embedding, list) and isinstance(embedding[0], list):
        return embedding[0]

    raise ValueError(f"Unexpected HF API response format: {type(embedding)}")


def _embed_via_local(query: str) -> list[float]:
    """Fallback: run SentenceTransformer locally if API is unavailable."""
    global _local_model
    if _local_model is None:
        logging.warning("Falling back to local SentenceTransformer (slow on limited CPU)")
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        _local_model = SentenceTransformer(model_name)
    embedding = _local_model.encode(query)
    return embedding.tolist()


def embed_query(query: str) -> list[float]:
    """
    Embed a query string into a 384-dim vector.
    Uses HuggingFace Inference API (fast, GPU-powered).
    Falls back to local SentenceTransformer if the API fails.
    """
    try:
        embedding = _embed_via_api(query)
        logging.info(f"Embedded query via HF API ({len(embedding)} dims)")
        return embedding
    except Exception as e:
        logging.warning(f"HF Inference API failed ({e}), falling back to local model")
        return _embed_via_local(query)
