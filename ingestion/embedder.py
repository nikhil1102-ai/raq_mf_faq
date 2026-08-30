import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Jina AI Embedding API
# ---------------------------------------------------------------------------
# Uses Jina's free embedding API instead of running SentenceTransformer
# locally. Railway's free-tier CPU takes 13s+ to run a neural network;
# Jina's GPU servers return embeddings in ~0.3s.
#
# Free tier: 1M tokens/month — more than enough for an FAQ bot.
# Model: jina-embeddings-v2-base-en (768 dims)
# ---------------------------------------------------------------------------

JINA_API_URL = "https://api.jina.ai/v1/embeddings"
JINA_MODEL = "jina-embeddings-v2-base-en"


def _get_jina_key() -> str:
    key = os.getenv("JINA_API_KEY", "")
    if not key:
        raise ValueError("JINA_API_KEY environment variable is not set")
    return key


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a list of text strings using Jina AI API (for ingestion)."""
    key = _get_jina_key()

    # Jina API accepts batches of up to 2048 texts
    response = requests.post(
        JINA_API_URL,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={
            "model": JINA_MODEL,
            "input": texts,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    # Extract embeddings in the correct order
    embeddings = [item["embedding"] for item in data["data"]]
    logging.info(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])} via Jina API")
    return embeddings
