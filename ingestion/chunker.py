"""
Text chunker for the mutual fund FAQ ingestion pipeline.

Uses semantic chunking: splits on section boundaries (double newlines),
prepends scheme identity to every chunk so each is self-contained,
then applies RecursiveCharacterTextSplitter for any sections that
exceed the chunk_size limit.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def chunk(text: str) -> list[str]:
    """
    Split parsed scheme text into self-contained, semantically meaningful chunks.
    
    Each chunk includes the scheme identity header so that it can be understood
    in isolation during retrieval.
    
    Strategy:
    1. Extract the scheme header line (first line in brackets)
    2. Split the remaining text on section boundaries (double newlines)
    3. Group small sections together if they fit within chunk_size
    4. For sections that exceed chunk_size, use RecursiveCharacterTextSplitter
    5. Prepend the scheme header to every resulting chunk
    """
    lines = text.strip().split("\n")
    
    # Extract the scheme header (first line, enclosed in brackets)
    header = ""
    content_start = 0
    if lines and lines[0].startswith("[Scheme:"):
        header = lines[0].strip()
        content_start = 1
    
    # Get remaining content (skip the header line and any blank lines after it)
    remaining_lines = lines[content_start:]
    remaining_text = "\n".join(remaining_lines).strip()
    
    # Split into sections on double newlines
    sections = [s.strip() for s in remaining_text.split("\n\n") if s.strip()]
    
    # Group sections into chunks, respecting the 500-char limit (minus header overhead)
    chunk_size = 500
    chunk_overlap = 50
    header_overhead = len(header) + 2  # +2 for "\n\n"
    effective_limit = chunk_size - header_overhead
    
    chunks = []
    current_group = []
    current_length = 0
    
    for section in sections:
        section_length = len(section)
        
        if section_length > effective_limit:
            # Flush the current group first
            if current_group:
                group_text = "\n\n".join(current_group)
                chunks.append(f"{header}\n\n{group_text}")
                current_group = []
                current_length = 0
            
            # This section is too large — split it with RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=effective_limit,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ". ", " "]
            )
            sub_chunks = splitter.split_text(section)
            for sub in sub_chunks:
                chunks.append(f"{header}\n\n{sub}")
        else:
            # Check if adding this section exceeds the limit
            new_length = current_length + section_length + (2 if current_group else 0)
            if new_length > effective_limit and current_group:
                # Flush current group
                group_text = "\n\n".join(current_group)
                chunks.append(f"{header}\n\n{group_text}")
                current_group = [section]
                current_length = section_length
            else:
                current_group.append(section)
                current_length = new_length
    
    # Flush any remaining group
    if current_group:
        group_text = "\n\n".join(current_group)
        chunks.append(f"{header}\n\n{group_text}")
    
    logging.info(f"Generated {len(chunks)} chunks from text ({len(text)} chars)")
    return chunks
