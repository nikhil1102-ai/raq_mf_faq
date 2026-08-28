import sys
import os
import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Ensure we can import from pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.qa_pipeline import answer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

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
