import time
import logging
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# IMPORT UPDATED HERE
from pipeline.intent_classifier import classify, refusal_response, personal_data_response
from retrieval.query_embedder import embed_query
from retrieval.retriever import retrieve
from pipeline.prompt_builder import build_prompt
from pipeline.llm_client import generate
from pipeline.response_formatter import format_response

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def answer(query: str) -> dict:
    start_time = time.time()
    logging.info(f"Processing query: '{query}'")
    
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
        
    # 2. Query Embedding
    query_vector = embed_query(query)
    
    # 3. Retrieval
    chunks = retrieve(query_vector)
    
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
    
    # 5. LLM Generation
    raw_answer = generate(messages)
    
    # 6. Response Formatting
    final_response = format_response(raw_answer, chunks)
    
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