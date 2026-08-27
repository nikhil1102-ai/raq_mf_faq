def build_prompt(query: str, chunks: list[dict]) -> list[dict]:
    system_prompt = (
        "You are a facts-only mutual fund FAQ assistant.\n"
        "Answer ONLY using information from the provided context.\n"
        "Do NOT provide investment advice, opinions, or fund comparisons.\n"
        "Keep your answer to a MAXIMUM of 3 sentences.\n"
        "Your answer MUST end with exactly this line:\n"
        "\"Source: <url> | Last updated: <date>\"\n"
        "If the context does not contain the answer, say:\n"
        "\"I don't have that information in my current data. Please visit the official AMC website.\""
    )

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Context {i}]\n"
            f"Source: {chunk['source_url']}\n"
            f"Last updated: {chunk['ingested_at']}\n"
            f"{chunk['text']}"
        )
    context_block = "\n\n".join(context_parts)

    user_message = f"Context:\n{context_block}\n\nQuestion: {query}"

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
