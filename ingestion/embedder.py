from sentence_transformers import SentenceTransformer
import logging

_model = None

def embed(texts: list[str]) -> list[list[float]]:
    global _model
    if _model is None:
        logging.info("Loading sentence-transformers/all-MiniLM-L6-v2 model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    
    embeddings = _model.encode(texts)
    logging.info(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")
    return embeddings.tolist()
