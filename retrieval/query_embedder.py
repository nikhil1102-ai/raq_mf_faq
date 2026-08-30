import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Jina AI Embedding API — Query Embedding
# ---------------------------------------------------------------------------
# Uses the same Jina model as the ingestion embedder to ensure consistency.
# Returns embeddings in ~0.3s vs 13s+ with local SentenceTransformer.
# ---------------------------------------------------------------------------

JINA_API_URL = "https://api.jina.ai/v1/embeddings"
JINA_MODEL = "jina-embeddings-v2-base-en"


def _get_jina_key() -> str:
    key = os.getenv("JINA_API_KEY", "")
    if not key:
        raise ValueError("JINA_API_KEY environment variable is not set")
    return key


def embed_query(query: str) -> list[float]:
    """Embed a single query string using Jina AI API."""
    key = _get_jina_key()

    response = requests.post(
        JINA_API_URL,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={
            "model": JINA_MODEL,
            "input": [query],
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    embedding = data["data"][0]["embedding"]
    logging.info(f"Embedded query via Jina API ({len(embedding)} dims)")
    return embedding
