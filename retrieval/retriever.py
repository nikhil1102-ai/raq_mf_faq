import os
import logging
from dotenv import load_dotenv
from retrieval.chroma_client import get_collection

load_dotenv()

def retrieve(query_vector: list[float], k: int = None) -> list[dict]:
    if k is None:
        k = int(os.getenv("TOP_K", 5))

    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(documents, metadatas, distances):
        if dist < 1.5:
            chunks.append({
                "text": doc,
                "source_url": meta.get("source_url", ""),
                "scheme_name": meta.get("scheme_name", ""),
                "ingested_at": meta.get("ingested_at", ""),
                "distance": dist
            })
        else:
            logging.info(f"Discarding chunk with distance {dist:.3f} (above threshold 1.5)")

    logging.info(f"Retrieved {len(chunks)} relevant chunks (k={k})")
    return chunks
