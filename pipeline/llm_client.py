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
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=messages,
            temperature=0.1,
            max_tokens=256,
            top_p=0.9
        )
        answer = response.choices[0].message.content.strip()
        logging.info(f"LLM response received ({len(answer)} chars)")
        return answer
    except Exception as e:
        raise LLMError(f"Groq API call failed: {e}") from e
