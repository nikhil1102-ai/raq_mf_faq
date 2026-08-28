import re
import logging

def format_response(raw_answer: str, chunks: list[dict]) -> dict:
    answer = raw_answer.strip()

    # Check if Source: line exists; append from chunk metadata if missing
    source_pattern = re.compile(r"Source:\s*https?://\S+", re.IGNORECASE)
    has_source = bool(source_pattern.search(answer))

    source_url = chunks[0]["source_url"] if chunks else ""
    last_updated = chunks[0]["ingested_at"] if chunks else ""

    if not has_source and source_url:
        answer = answer.rstrip() + f"\n\nSource: {source_url} | Last updated: {last_updated}"
        logging.info("Source line was missing from LLM response; appended from metadata.")

    # Extract just the answer portion (before the Source line for clean display)
    answer_match = re.split(r"\n*\s*Source:", answer, flags=re.IGNORECASE)
    answer_text = answer_match[0].strip() if len(answer_match) > 1 else answer

    return {
        "type": "factual",
        "answer": answer_text,
        "source_url": source_url,
        "last_updated": last_updated,
        "full_text": answer
    }
