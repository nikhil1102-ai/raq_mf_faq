import os
import sys
import time
import argparse
import logging
from datetime import datetime

# Add project root to sys.path to allow imports from retrieval/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.schemes import SCHEMES
from ingestion.scraper import scrape
from ingestion.parser import parse
from ingestion.chunker import chunk
from ingestion.embedder import embed
from retrieval.chroma_client import get_collection

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Mutual Fund FAQ Ingestion Pipeline")
    parser.add_argument("--mode", choices=["full", "daily"], default="full",
                        help="full: re-ingest all schemes. daily: same but fail-fast on errors.")
    parser.add_argument("--source", choices=["web", "processed"], default="web",
                        help="web: scrape from Groww. processed: re-chunk from data/processed/*.txt files.")
    parser.add_argument("--clear", action="store_true",
                        help="Clear the ChromaDB collection before ingesting.")
    args = parser.parse_args()

    logging.info(f"Starting ingestion pipeline: mode={args.mode}, source={args.source}, clear={args.clear}")
    start_time_total = time.time()

    collection = get_collection()

    # Clear collection if requested
    if args.clear:
        existing_count = collection.count()
        if existing_count > 0:
            logging.info(f"Clearing {existing_count} existing documents from collection.")
            # ChromaDB: delete all by getting all IDs
            all_ids = collection.get()["ids"]
            if all_ids:
                collection.delete(ids=all_ids)
            logging.info("Collection cleared.")
        else:
            logging.info("Collection is already empty.")

    total_chunks = 0
    failures = []

    for scheme in SCHEMES:
        start_time_scheme = time.time()
        slug = scheme["slug"]
        logging.info(f"Processing scheme: {scheme['name']}")

        try:
            if args.source == "processed":
                # Read from existing processed text files
                processed_path = os.path.join("data", "processed", f"{slug}.txt")
                if not os.path.exists(processed_path):
                    raise FileNotFoundError(f"Processed file not found: {processed_path}")
                with open(processed_path, "r", encoding="utf-8") as f:
                    text = f.read()
                logging.info(f"Loaded processed text from {processed_path} ({len(text)} chars)")
            else:
                # 1. Scrape
                html = scrape(scheme["url"], slug)

                # 2. Parse
                text = parse(html, scheme)

            # 3. Chunk
            chunks = chunk(text)
            logging.info(f"Generated {len(chunks)} chunks.")

            if not chunks:
                raise ValueError("No chunks generated from parsed text.")

            # 4. Embed
            embeddings = embed(chunks)

            # 5. Build IDs and Metadata
            ids = [f"{slug}_{i}" for i in range(len(chunks))]
            today = datetime.now().strftime("%Y-%m-%d")

            metadatas = [
                {
                    "source_url": scheme["url"],
                    "scheme_name": scheme["name"],
                    "amc": scheme["amc"],
                    "category": scheme["category"],
                    "ingested_at": today
                }
                for _ in chunks
            ]

            # 6. Upsert
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )

            total_chunks += len(chunks)
            elapsed = time.time() - start_time_scheme
            logging.info(f"Successfully upserted {len(chunks)} chunks for {slug} in {elapsed:.2f}s.")

        except Exception as e:
            logging.error(f"Failed to process scheme {slug}: {e}")
            failures.append(slug)
            if args.mode == "daily":
                logging.error("Daily ingestion mode requires all schemes to succeed. Exiting with error.")
                sys.exit(1)

    total_elapsed = time.time() - start_time_total

    print("\n--- Ingestion Summary ---")
    print(f"Total time: {total_elapsed:.2f}s")
    print(f"Total chunks upserted: {total_chunks}")
    print(f"Total documents in collection: {collection.count()}")
    if failures:
        print(f"Failures ({len(failures)}): {', '.join(failures)}")
        sys.exit(1)
    else:
        print("All schemes processed successfully.")


if __name__ == "__main__":
    main()
