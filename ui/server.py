import sys
import os
import logging
import traceback
import threading

from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Ensure we can import from pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.qa_pipeline import answer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()


# --- Auto-Ingest on Startup ---
@app.on_event("startup")
def auto_ingest_if_empty():
    """Check if ChromaDB is empty on startup and auto-ingest from processed files."""
    try:
        from retrieval.chroma_client import get_collection
        collection = get_collection()
        doc_count = collection.count()
        logging.info(f"ChromaDB collection has {doc_count} documents.")

        if doc_count == 0:
            logging.info("ChromaDB is empty — starting auto-ingestion in background thread...")

            def _startup_ingest():
                global _ingest_running
                _ingest_running = True
                try:
                    from ingestion.ingest import main as ingest_main
                    original_argv = sys.argv
                    sys.argv = ["ingest.py", "--mode", "full", "--source", "processed"]
                    try:
                        ingest_main()
                    finally:
                        sys.argv = original_argv
                    logging.info("Auto-ingestion completed successfully.")
                except Exception as e:
                    logging.error(f"Auto-ingestion failed: {e}")
                    logging.error(traceback.format_exc())
                finally:
                    _ingest_running = False

            thread = threading.Thread(target=_startup_ingest, daemon=True)
            thread.start()
        else:
            logging.info("ChromaDB already has data — skipping auto-ingestion.")
    except Exception as e:
        logging.error(f"Auto-ingest check failed: {e}")
        logging.error(traceback.format_exc())


# --- CORS Middleware ---
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve paths relative to the project root, not the CWD
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(PROJECT_ROOT, "ui", "static")
INDEX_HTML = os.path.join(PROJECT_ROOT, "ui", "index.html")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class Query(BaseModel):
    query: str


@app.get("/")
def root():
    return FileResponse(INDEX_HTML)


@app.get("/api/health")
def health():
    """Health check endpoint for Railway."""
    return {"status": "ok"}


@app.post("/api/ask")
def ask(q: Query):
    try:
        response = answer(q.query)

        # Ensure 'type' key is always present
        if "type" not in response:
            if "answer" in response:
                response["type"] = "factual"
            elif "message" in response:
                response["type"] = "advisory"

        return response

    except Exception as e:
        logging.error(f"Error processing query '{q.query}': {e}")
        logging.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "type": "error",
                "message": "An internal error occurred while processing your request. Please try again."
            }
        )


# --- Ingestion Trigger Endpoint ---
# Runs the ingestion pipeline inside the app process (packages are available here)
_ingest_lock = threading.Lock()
_ingest_running = False


@app.post("/api/ingest/trigger")
def trigger_ingest(authorization: str = Header(default=None)):
    """Trigger the ingestion pipeline. Protected by INGEST_API_KEY."""
    global _ingest_running

    # Auth check
    expected_key = os.getenv("INGEST_API_KEY")
    if expected_key:
        if not authorization or authorization != f"Bearer {expected_key}":
            raise HTTPException(status_code=401, detail="Unauthorized")

    if _ingest_running:
        return JSONResponse(
            status_code=409,
            content={"status": "already_running", "message": "Ingestion is already in progress."}
        )

    def run_ingest():
        global _ingest_running
        _ingest_running = True
        try:
            from ingestion.ingest import main as ingest_main
            # Monkey-patch sys.argv so argparse doesn't fail
            original_argv = sys.argv
            sys.argv = ["ingest.py", "--mode", "daily", "--source", "processed"]
            try:
                ingest_main()
            finally:
                sys.argv = original_argv
            logging.info("Ingestion completed successfully.")
        except Exception as e:
            logging.error(f"Ingestion failed: {e}")
            logging.error(traceback.format_exc())
        finally:
            _ingest_running = False

    thread = threading.Thread(target=run_ingest, daemon=True)
    thread.start()

    return {"status": "started", "message": "Ingestion pipeline started in the background."}

