import os
import logging
import groq
from dotenv import load_dotenv

load_dotenv()

class LLMError(Exception):
    pass

_client = None

def _get_client() -> groq.Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise LLMError("GROQ_API_KEY is not set. Please update your .env file.")
        _client = groq.Groq(api_key=api_key)
    return _client

def generate(messages: list[dict]) -> str:
    client = _get_client()
    try:
        # Retry up to 2 times if the model returns empty content
        for attempt in range(2):
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",   # or "openai/gpt-oss-120b" for higher quality
                messages=messages,
                temperature=0.1,
                max_tokens=512,
            )
            answer = response.choices[0].message.content.strip()
            logging.info(f"LLM response received ({len(answer)} chars) [attempt {attempt + 1}]")
            if answer:
                return answer
            logging.warning(f"LLM returned empty response on attempt {attempt + 1}, retrying...")
        # If still empty after retries, return a safe fallback
        logging.error("LLM returned empty response after all retries.")
        return "I don't have that information in my current data. Please visit the official AMC website."
    except Exception as e:
        raise LLMError(f"Groq API call failed: {e}") from e
