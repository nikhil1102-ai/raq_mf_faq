import time
import logging
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORT UPDATED HERE
from pipeline.intent_classifier import classify, refusal_response, personal_data_response, statement_response
from retrieval.query_embedder import embed_query
from retrieval.retriever import retrieve
from pipeline.prompt_builder import build_prompt
from pipeline.llm_client import generate
from pipeline.response_formatter import format_response

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Simple query-level cache ---
# Stores (result, timestamp) keyed by normalized query string.
# FAQ bots receive many repeated questions — this bypasses embed+retrieve+LLM entirely.
_cache: dict = {}
_CACHE_TTL = 3600  # seconds (1 hour)
_CACHE_MAX = 128

def _get_cached(query: str):
    key = " ".join(query.lower().split())
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < _CACHE_TTL:
        return entry["result"]
    return None

def _set_cache(query: str, result: dict):
    key = " ".join(query.lower().split())
    if len(_cache) >= _CACHE_MAX:
        # Evict the oldest entry
        oldest = min(_cache, key=lambda k: _cache[k]["ts"])
        del _cache[oldest]
    _cache[key] = {"result": result, "ts": time.time()}

def answer(query: str) -> dict:
    start_time = time.time()
    logging.info(f"Processing query: '{query}'")

    # Cache check — skip for advisory/personal (non-deterministic intent not needed)
    cached = _get_cached(query)
    if cached is not None:
        logging.info(f"Cache HIT for query: '{query}'")
        return cached
    
    # 1. Intent Classification
    intent = classify(query)
    
    if intent == "ADVISORY":
        elapsed = time.time() - start_time
        logging.info(f"Query processed in {elapsed:.2f}s (Advisory)")
        return {
            "type": "advisory",
            "message": refusal_response()
        }
        
    # NEW BLOCK FOR PERSONAL DATA
    if intent == "PERSONAL":
        elapsed = time.time() - start_time
        logging.info(f"Query processed in {elapsed:.2f}s (Personal)")
        return {
            "type": "advisory", # Keeping type as advisory so the UI correctly shows the warning bubble
            "message": personal_data_response()
        }

    # NEW BLOCK FOR STATEMENT QUERIES
    if intent == "STATEMENT":
        elapsed = time.time() - start_time
        logging.info(f"Query processed in {elapsed:.2f}s (Statement)")
        return {
            "type": "advisory", # Keeping type as advisory so the UI correctly shows the warning bubble
            "message": statement_response()
        }
        
    # 2. Query Embedding
    t0 = time.time()
    query_vector = embed_query(query)
    t1 = time.time()
    logging.info(f"  [TIMING] embed_query: {t1 - t0:.2f}s")
    
    # 3. Retrieval
    chunks = retrieve(query_vector)
    t2 = time.time()
    logging.info(f"  [TIMING] retrieve: {t2 - t1:.2f}s")
    
    if not chunks:
        elapsed = time.time() - start_time
        logging.info(f"Query processed in {elapsed:.2f}s (No relevant chunks)")
        return {
            "type": "factual",
            "answer": "I don't have that information in my current data. Please visit the official AMC website.",
            "source_url": "",
            "last_updated": "",
            "full_text": "I don't have that information in my current data. Please visit the official AMC website."
        }
        
    # 4. Prompt Building
    messages = build_prompt(query, chunks)
    t3 = time.time()
    logging.info(f"  [TIMING] build_prompt: {t3 - t2:.2f}s")
    
    # 5. LLM Generation
    raw_answer = generate(messages)
    t4 = time.time()
    logging.info(f"  [TIMING] llm_generate: {t4 - t3:.2f}s")
    
    # 6. Response Formatting
    final_response = format_response(raw_answer, chunks)
    t5 = time.time()
    logging.info(f"  [TIMING] format_response: {t5 - t4:.2f}s")

    # Cache the result for repeated queries
    _set_cache(query, final_response)

    elapsed = time.time() - start_time
    logging.info(f"Query processed in {elapsed:.2f}s (Factual)")

    return final_response

if __name__ == "__main__":
    print("\n--- Test Advisory Query ---")
    res1 = answer("Should I invest in this fund?")
    print(res1)
    
    print("\n--- Test Personal Query ---")
    res2 = answer("How much funds are invested on my PAN?")
    print(res2)
    
    print("\n--- Test Factual Query ---")
    res3 = answer("What is the expense ratio of ICICI Large Cap?")
    print(res3)