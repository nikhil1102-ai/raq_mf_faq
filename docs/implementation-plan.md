# Implementation Plan: Mutual Fund FAQ Assistant (RAG-Based)

> **Project:** RAG-MF_FAQ | **LLM:** Groq `openai/gpt-oss-20b` | **Vector DB:** ChromaDB | **Scheduler:** GitHub Actions Daily Cron (Option B)

---

## Overview

This document provides a phase-wise, task-level implementation plan for building the Mutual Fund FAQ Assistant. The project is broken into **6 phases**, each with clear objectives, deliverables, acceptance criteria, and estimated effort. Phases are ordered by dependency — each phase builds on the previous one.

```
Phase 1 → Project Setup & Environment
Phase 2 → Data Ingestion Pipeline
Phase 3 → RAG Query Pipeline
Phase 4 → GitHub Actions Daily Scheduler
Phase 5 → User Interface (UI)
Phase 6 → Integration, Testing & Hardening
```

---

## Phase Summary

| Phase | Name | Key Deliverable | Effort |
|-------|------|-----------------|--------|
| 1 | Project Setup & Environment | Repo, deps, config, ChromaDB init | 0.5 day |
| 2 | Data Ingestion Pipeline | Scraper → Parser → Chunker → Embedder → ChromaDB | 2 days |
| 3 | RAG Query Pipeline | Intent classifier, retriever, prompt builder, LLM, formatter | 2 days |
| 4 | GitHub Actions Daily Scheduler | `daily_ingest.yml` workflow, caching, alerting | 1 day |
| 5 | User Interface (HTML + TailwindCSS) | Assemble stitch components → `ui/index.html` + FastAPI backend bridge | 1.5 days |
| 6 | Integration, Testing & Hardening | End-to-end tests, edge cases, README, final review | 1.5 days |

**Total Estimated Effort: ~8.5 working days**

---

## Phase 1: Project Setup & Environment

### Objective
Establish the project skeleton, dependency management, configuration, and a working ChromaDB connection before any functional code is written.

### Tasks

#### 1.1 — Repository Structure
- [ ] Create the directory layout as defined in `architecture.md §6`
  ```
  RAG-MF_FAQ/
  ├── .github/workflows/
  ├── docs/
  ├── data/raw/   data/processed/
  ├── ingestion/
  ├── retrieval/
  ├── pipeline/
  ├── ui/
  └── chroma_store/
  ```
- [ ] Initialise a Git repository (`git init`)
- [ ] Create `.gitignore` — exclude `.env`, `chroma_store/`, `__pycache__/`, `*.pyc`, `data/raw/`

#### 1.2 — Dependencies
- [ ] Create `requirements.txt` with pinned versions:

  ```
  requests==2.31.0
  beautifulsoup4==4.12.3
  langchain==0.2.x
  langchain-community==0.2.x
  sentence-transformers==3.x
  chromadb==0.5.x
  groq==0.9.x
  streamlit==1.35.x
  python-dotenv==1.0.x
  ```
- [ ] Create a virtual environment: `python -m venv .venv`
- [ ] Install all dependencies: `pip install -r requirements.txt`

#### 1.3 — Configuration & Secrets
- [ ] Create `.env.example`:
  ```
  GROQ_API_KEY=your_groq_api_key_here
  CHROMA_PERSIST_DIR=./chroma_store
  COLLECTION_NAME=mf_faq_corpus
  EMBEDDING_MODEL=all-MiniLM-L6-v2
  TOP_K=5
  ```
- [ ] Create `.env` (from `.env.example`) and populate with real `GROQ_API_KEY`
- [ ] Create `retrieval/chroma_client.py` — initialises a persistent ChromaDB client and returns/creates the `mf_faq_corpus` collection

#### 1.4 — Scheme Registry
- [ ] Create `ingestion/schemes.py` — a Python list of all 6 scheme configs:

  ```python
  SCHEMES = [
      {"slug": "icici_large_cap",    "name": "ICICI Prudential Large Cap Fund – Direct Growth",             "amc": "ICICI Prudential", "category": "Large Cap",  "url": "https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth"},
      {"slug": "icici_flexicap",     "name": "ICICI Prudential Flexicap Fund – Direct Growth",             "amc": "ICICI Prudential", "category": "Flexi Cap",  "url": "https://groww.in/mutual-funds/icici-prudential-flexicap-fund-direct-growth"},
      {"slug": "icici_multicap",     "name": "ICICI Prudential Multicap Fund – Direct Growth",             "amc": "ICICI Prudential", "category": "Multi Cap",  "url": "https://groww.in/mutual-funds/icici-prudential-multicap-fund-direct-growth"},
      {"slug": "nippon_momentum_50", "name": "Nippon India Nifty 500 Momentum 50 Index Fund – Direct Growth", "amc": "Nippon India",    "category": "Index",      "url": "https://groww.in/mutual-funds/nippon-india-nifty-500-momentum-50-index-fund-direct-growth"},
      {"slug": "nippon_large_cap",   "name": "Nippon India Large Cap Fund – Direct Growth",                "amc": "Nippon India",    "category": "Large Cap",  "url": "https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth"},
      {"slug": "nippon_elss",        "name": "Nippon India Tax Saver ELSS Fund – Direct Growth",           "amc": "Nippon India",    "category": "ELSS",       "url": "https://groww.in/mutual-funds/nippon-india-elss-tax-saver-fund-direct-growth"},
  ]
  ```

### Acceptance Criteria
- [ ] All directories exist; `.gitignore` is correct
- [ ] `pip install -r requirements.txt` completes without errors
- [ ] `chroma_client.py` can create and return the `mf_faq_corpus` collection without error
- [ ] `.env.example` committed; `.env` ignored by Git

---

## Phase 2: Data Ingestion Pipeline

### Objective
Build the automated pipeline that scrapes, normalises, chunks, embeds, and upserts all 6 scheme pages into ChromaDB. This is the corpus-building layer.

### Tasks

#### 2.1 — Web Scraper (`ingestion/scraper.py`)
- [ ] Function: `scrape(url: str) -> str` — fetches raw HTML using `requests` with a browser-like `User-Agent` header
- [ ] Implement retry logic (3 attempts, exponential back-off) for transient failures
- [ ] Return raw HTML string; raise `ScraperError` on failure after retries
- [ ] Save raw HTML to `data/raw/{slug}.html` for debugging

#### 2.2 — HTML Parser / Normaliser (`ingestion/parser.py`)
- [ ] Function: `parse(html: str, scheme: dict) -> str` — extracts factual text sections from Groww page HTML
- [ ] Target sections to extract (use CSS selectors / tag inspection):
  - Expense Ratio
  - Exit Load
  - Minimum SIP / Lump Sum amount
  - Riskometer classification
  - Benchmark index
  - ELSS lock-in period (where applicable)
  - Fund manager name
  - AUM
  - NAV
- [ ] Strip all HTML tags, normalise whitespace, remove boilerplate navigation text
- [ ] Prepend scheme metadata header to the cleaned text:
  ```
  [Scheme: ICICI Prudential Large Cap Fund | AMC: ICICI Prudential | Category: Large Cap | Source: <url>]
  ```
- [ ] Save cleaned text to `data/processed/{slug}.txt`

#### 2.3 — Text Chunker (`ingestion/chunker.py`)
- [ ] Function: `chunk(text: str) -> list[str]` — uses LangChain `RecursiveCharacterTextSplitter`
- [ ] Config: `chunk_size=500`, `chunk_overlap=50`, `separators=["\n\n", "\n", ". ", " "]`
- [ ] Return list of text chunks

#### 2.4 — Embedding Generator (`ingestion/embedder.py`)
- [ ] Load `sentence-transformers/all-MiniLM-L6-v2` model (cached after first load)
- [ ] Function: `embed(texts: list[str]) -> list[list[float]]` — batch-encodes chunks
- [ ] Log embedding dimension for verification (should be 384)

#### 2.5 — ChromaDB Upsert (`ingestion/ingest.py`)
- [ ] Orchestrates the full pipeline for all schemes in `SCHEMES`
- [ ] For each scheme:
  1. Scrape HTML
  2. Parse & clean
  3. Chunk text
  4. Generate embeddings
  5. Build chunk IDs: `{slug}_{chunk_index}` (deterministic, prevents duplicates)
  6. Build metadata per chunk: `source_url`, `scheme_name`, `amc`, `category`, `ingested_at` (today's date `YYYY-MM-DD`)
  7. Call `collection.upsert(ids, embeddings, documents, metadatas)`
- [ ] Support `--mode daily` CLI flag for use by GitHub Actions
- [ ] Log: scheme name, chunks count, upsert status, total time per scheme
- [ ] Print summary at end: total chunks upserted, total time, any failures

### Acceptance Criteria
- [ ] Running `python ingestion/ingest.py` successfully scrapes all 6 schemes
- [ ] ChromaDB collection `mf_faq_corpus` contains ~150–240 documents after ingest
- [ ] Each chunk has correct metadata (`source_url`, `scheme_name`, `amc`, `category`, `ingested_at`)
- [ ] Re-running ingest does **not** duplicate chunks (upsert idempotency verified)
- [ ] `data/raw/*.html` and `data/processed/*.txt` files are created for all 6 schemes

---

## Phase 3: RAG Query Pipeline

### Objective
Build the query-time pipeline: intent classification, semantic retrieval from ChromaDB, prompt construction, LLM generation, and response formatting.

### Tasks

#### 3.1 — Intent Classifier (`pipeline/intent_classifier.py`)
- [ ] Function: `classify(query: str) -> Literal["FACTUAL", "ADVISORY"]`
- [ ] Rule-based approach: match against an advisory keyword/pattern list:
  ```python
  ADVISORY_PATTERNS = [
      "should i", "which is better", "recommend", "advice",
      "opinion", "worth investing", "good fund", "compare returns",
      "outperform", "best fund", "suggest", "is it safe to invest"
  ]
  ```
- [ ] Case-insensitive match; if any pattern found → `ADVISORY`, else → `FACTUAL`
- [ ] Log classification decision for observability

#### 3.2 — Refusal Response (`pipeline/intent_classifier.py`)
- [ ] Function: `refusal_response() -> str` — returns a polite, pre-defined refusal:
  ```
  I can only provide factual information about mutual fund schemes. 
  For investment guidance, please consult a SEBI-registered advisor or 
  visit AMFI's investor education portal: https://www.amfiindia.com/investor-corner/knowledge-center
  
  Facts-only. No investment advice.
  ```

#### 3.3 — Query Embedder (`retrieval/query_embedder.py`)
- [ ] Load the same `all-MiniLM-L6-v2` model used during ingestion (shared cache)
- [ ] Function: `embed_query(query: str) -> list[float]`

#### 3.4 — Retriever (`retrieval/retriever.py`)
- [ ] Function: `retrieve(query_vector: list[float], k: int = 5) -> list[dict]`
- [ ] Calls `collection.query(query_embeddings=[query_vector], n_results=k, include=["documents", "metadatas", "distances"])`
- [ ] Returns list of dicts: `{text, source_url, scheme_name, ingested_at, distance}`
- [ ] Filter: only include chunks with cosine distance < 0.8 (discard irrelevant results)

#### 3.5 — Prompt Builder (`pipeline/prompt_builder.py`)
- [ ] Function: `build_prompt(query: str, chunks: list[dict]) -> list[dict]` — returns OpenAI-style messages list
- [ ] System prompt (strict, non-negotiable):
  ```
  You are a facts-only mutual fund FAQ assistant.
  Answer ONLY using information from the provided context.
  Do NOT provide investment advice, opinions, or fund comparisons.
  Keep your answer to a MAXIMUM of 3 sentences.
  Your answer MUST end with exactly this line:
  "Source: <url> | Last updated: <date>"
  If the context does not contain the answer, say:
  "I don't have that information in my current data. Please visit the official AMC website."
  ```
- [ ] Context block: concatenate top-k chunk texts with source URLs
- [ ] User message: the original query

#### 3.6 — Groq LLM Client (`pipeline/llm_client.py`)
- [ ] Initialise `groq.Groq(api_key=os.getenv("GROQ_API_KEY"))`
- [ ] Function: `generate(messages: list[dict]) -> str`
- [ ] Model: `qwen-3-32b`, Temperature: `0.1`, Max tokens: `256`, Top-P: `0.9`
- [ ] Wrap in try/except; raise `LLMError` on API failure

#### 3.7 — Response Formatter (`pipeline/response_formatter.py`)
- [ ] Function: `format_response(raw_answer: str, chunks: list[dict]) -> dict`
- [ ] Validate that the response contains a `Source:` line; append from chunk metadata if missing
- [ ] Return structured dict:
  ```python
  {
    "answer": "...",           # The ≤3-sentence answer
    "source_url": "...",       # Citation link
    "last_updated": "YYYY-MM-DD",  # From chunk ingested_at
    "full_text": "...\n\nSource: ... | Last updated: ..."
  }
  ```

#### 3.8 — Main Pipeline Orchestrator (`pipeline/qa_pipeline.py`)
- [ ] Function: `answer(query: str) -> dict`
- [ ] Wires all components:
  1. `classify(query)` → if ADVISORY return `refusal_response()`
  2. `embed_query(query)` → query vector
  3. `retrieve(query_vector)` → top-k chunks
  4. `build_prompt(query, chunks)` → messages
  5. `generate(messages)` → raw answer
  6. `format_response(raw_answer, chunks)` → final dict
- [ ] Log end-to-end latency per query

### Acceptance Criteria
- [ ] `classify("Should I invest in this fund?")` returns `"ADVISORY"`
- [ ] `classify("What is the expense ratio of ICICI Large Cap?")` returns `"FACTUAL"`
- [ ] Factual query returns an answer ≤ 3 sentences with a valid source URL
- [ ] Response always includes `Last updated: YYYY-MM-DD` footer
- [ ] Advisory query returns the polite refusal with AMFI link
- [ ] If no relevant chunks found (distance > 0.8), fallback message is returned

---

## Phase 4: GitHub Actions Daily Scheduler

### Objective
Automate the daily ingestion pipeline using GitHub Actions so the ChromaDB corpus is refreshed every day at 00:00 UTC without any manual intervention.

### Tasks

#### 4.1 — Workflow File (`.github/workflows/daily_ingest.yml`)
- [ ] Create the complete workflow YAML:
  ```yaml
  name: Daily Corpus Refresh
  on:
    schedule:
      - cron: "0 0 * * *"   # 00:00 UTC = 05:30 IST daily
    workflow_dispatch:        # Manual trigger from GitHub UI
  jobs:
    ingest:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with: { python-version: "3.11" }
        - uses: actions/cache@v4
          with:
            path: ~/.cache/pip
            key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
        - run: pip install -r requirements.txt
        - uses: actions/cache@v4
          with:
            path: chroma_store/
            key: chroma-store-${{ github.run_id }}
            restore-keys: chroma-store-
        - run: python ingestion/ingest.py --mode daily
          env: { GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }} }
        - uses: actions/upload-artifact@v4
          with:
            name: chroma-store-${{ github.run_number }}
            path: chroma_store/
            retention-days: 7
        - if: failure()
          run: echo "::error::Daily ingestion failed — ChromaDB may be stale!"
  ```

#### 4.2 — GitHub Repository Configuration
- [ ] Add `GROQ_API_KEY` as a GitHub Actions Secret:
  `Settings → Secrets and variables → Actions → New repository secret`
- [ ] Verify the workflow appears under `Actions` tab after push
- [ ] Run the workflow manually once via `workflow_dispatch` to validate the first full ingestion

#### 4.3 — Ingest Script CLI Flag
- [ ] Ensure `ingestion/ingest.py` supports `--mode daily` argument:
  ```python
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("--mode", choices=["full", "daily"], default="full")
  args = parser.parse_args()
  ```
- [ ] In `daily` mode: log run date/time at start and end; exit with non-zero code on any scheme failure (triggers GitHub Actions failure alert)

#### 4.4 — Failure Monitoring
- [ ] Add GitHub Actions email notification (enabled by default for workflow failures on the repository owner's account)
- [ ] Document the monitoring approach in `README.md`

### Acceptance Criteria
- [ ] Workflow file is valid YAML (verified with `yamllint`)
- [ ] Manual `workflow_dispatch` run completes successfully in GitHub Actions
- [ ] ChromaDB artifact is uploaded and visible in the GitHub Actions run summary
- [ ] A simulated failure (bad URL in test) triggers the `::error::` annotation
- [ ] `GROQ_API_KEY` is not visible in any workflow log output

---

## Phase 5: User Interface (HTML + TailwindCSS + FastAPI)

### Objective
Assemble the pre-built stitch UI components from `stitch_mutual_fund_faq_assistant/` into a single production-ready `ui/index.html`, wire it to the RAG backend via a lightweight **FastAPI** JSON endpoint, and ensure all required UX behaviours (welcome state, factual answer display, refusal handling, mobile view) work end-to-end.

### Frontend Stack (from Stitch Components)

| Technology | Source | Purpose |
|------------|--------|--------|
| **HTML5** | All `code.html` stitch files | Page structure & component markup |
| **TailwindCSS CDN** | `cdn.tailwindcss.com?plugins=forms,container-queries` | Utility-first styling |
| **Inter** (Google Fonts) | Font import in stitch HTML | Typography |
| **Material Symbols** (Google Fonts) | Icon font import in stitch HTML | UI icons (`smart_toy`, `analytics`, `lock_clock`, etc.) |
| **Vanilla JavaScript** | Custom — to be authored in Phase 5 | Fetch API calls, state management, UI transitions |
| **FastAPI** | Python backend | Serves `index.html` + exposes `/api/ask` JSON endpoint |

### Stitch Component Inventory

| Directory | Purpose | Key Elements |
|-----------|---------|-------------|
| `mutual_fund_chatbot_assistant/` | **Master layout shell** — the primary template to build from | Desktop sidebar, TopAppBar, disclaimer banner, chat canvas, docked input bar, footer |
| `welcome_faq_assistant_1/` | **Welcome state (variant 1)** | Assistant avatar, headline "How can I help?", 3-column bento example cards |
| `welcome_faq_assistant_2/` | **Welcome state (variant 2)** | Alternative layout for the initial empty state |
| `chat_factual_answer_1/` | **Factual answer bubble (variant 1)** | AI response bubble with source chip and last-updated caption |
| `chat_factual_answer_2/` | **Factual answer bubble (variant 2)** | Alternative answer display layout |
| `chat_special_states_1/` | **Special states (variant 1)** | Thinking/loading skeleton, empty state, error state |
| `chat_special_states_2/` | **Special states (variant 2)** | Alternative error / refusal display |
| `cognitive_finance_logic_1/` | **Design system spec** (`DESIGN.md`) | Full token reference — colours, typography, spacing, component guidelines |
| `cognitive_finance_logic_2/` | **Design system spec (variant 2)** | Extended component guidelines |
| `mobile_chat_view/` | **Mobile responsive layout** | Full-height mobile chat, bottom-docked input, hamburger nav |

### Tasks

#### 5.1 — Assemble Master HTML (`ui/index.html`)
- [ ] Start from `mutual_fund_chatbot_assistant/code.html` as the base shell
- [ ] Adopt the **Tailwind theme config** (colours, typography, spacing) verbatim from the stitch file — do **not** re-define tokens
- [ ] Merge the welcome state markup from `welcome_faq_assistant_1/code.html` into the chat canvas region
- [ ] Integrate the sidebar scheme directory with the correct 6 schemes:
  - ICICI Prudential Large Cap Fund – Direct Growth
  - ICICI Prudential Flexicap Fund – Direct Growth
  - ICICI Prudential Multicap Fund – Direct Growth
  - Nippon India Nifty 500 Momentum 50 Index Fund – Direct Growth
  - Nippon India Large Cap Fund – Direct Growth
  - Nippon India Tax Saver ELSS Fund – Direct Growth
- [ ] Ensure the permanent disclaimer banner (`tertiary-fixed` background) is always visible below the TopAppBar
- [ ] Integrate `mobile_chat_view/code.html` responsive breakpoint logic for screens < `md` (768px)

#### 5.2 — Example Question Cards
- [ ] Use the 3-column bento card layout from `welcome_faq_assistant_1/code.html`
- [ ] Update card content to the 3 canonical example queries:
  1. *"What is the expense ratio of ICICI Prudential Flexicap Fund?"*  (icon: `analytics`)
  2. *"What is the lock-in period for Nippon India Tax Saver ELSS Fund?"*  (icon: `lock_clock`)
  3. *"How can I download my capital-gains statement?"*  (icon: `description`)
- [ ] On card click: populate the chat input field with the question text and auto-submit

#### 5.3 — JavaScript State Machine (`ui/app.js`)
- [ ] **States:** `WELCOME` → `LOADING` → `ANSWER` | `REFUSAL` | `ERROR`
- [ ] State transitions:
  - `WELCOME` (initial) — show welcome canvas, hide chat history
  - `LOADING` — hide example cards; show thinking skeleton from `chat_special_states_1/code.html`
  - `ANSWER` — render AI bubble from `chat_factual_answer_1/code.html` pattern
  - `REFUSAL` — render refusal bubble from `chat_special_states_2/code.html` pattern
  - `ERROR` — render error state from `chat_special_states_1/code.html` pattern
- [ ] **Send logic** (`sendMessage()`):
  ```javascript
  async function sendMessage(query) {
    setState('LOADING');
    appendUserBubble(query);
    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      if (data.type === 'factual') {
        appendAssistantBubble(data.answer, data.source_url, data.last_updated);
        setState('ANSWER');
      } else {
        appendRefusalBubble(data.message);
        setState('REFUSAL');
      }
    } catch (e) {
      appendErrorBubble();
      setState('ERROR');
    }
  }
  ```
- [ ] Wire card clicks and the send button to `sendMessage()`
- [ ] Auto-scroll chat area to the latest message after each response

#### 5.4 — Factual Answer Bubble
- [ ] Implement `appendAssistantBubble(answer, sourceUrl, lastUpdated)` following `chat_factual_answer_1/code.html`:
  - AI bubble: `surface-container-low` background, `border-l-4 border-primary`, `rounded-xl`
  - Answer text in `body-md` / `on-surface`
  - Source chip: small `surface-variant` pill with a clickable `<a>` tag to the source URL
  - Footer caption: `caption-sm` `on-surface-variant` — *"Last updated: YYYY-MM-DD"*

#### 5.5 — Refusal & Special-State Bubbles
- [ ] Implement `appendRefusalBubble(message)` following `chat_special_states_2/code.html`:
  - Amber/tertiary-fixed tinted bubble with warning icon
  - Refusal text + AMFI educational link: `https://www.amfiindia.com/investor-corner/knowledge-center`
  - Footer: *"Facts-only. No investment advice."*
- [ ] Implement `appendErrorBubble()` for network/API failures:
  - Error-container tinted bubble with `error` icon
  - Message: *"Something went wrong. Please try again."*
- [ ] Implement thinking skeleton (pulsing placeholder) for the `LOADING` state from `chat_special_states_1/code.html`

#### 5.6 — FastAPI Backend Bridge (`ui/server.py`)
- [ ] Create a FastAPI app that:
  - Serves `ui/index.html` at `GET /`
  - Serves `ui/app.js` as a static file
  - Exposes `POST /api/ask` endpoint:
    ```python
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    from pydantic import BaseModel
    from pipeline.qa_pipeline import answer

    app = FastAPI()
    app.mount("/static", StaticFiles(directory="ui/static"), name="static")

    class Query(BaseModel):
        query: str

    @app.get("/")
    def root():
        return FileResponse("ui/index.html")

    @app.post("/api/ask")
    def ask(q: Query):
        return answer(q.query)   # returns dict with type, answer, source_url, last_updated
    ```
- [ ] Add `fastapi` and `uvicorn[standard]` to `requirements.txt`
- [ ] Run with: `uvicorn ui.server:app --reload --port 8000`

#### 5.7 — Directory Structure for UI
```
ui/
├── index.html          # Assembled from stitch components
├── app.js              # State machine + Fetch API logic
├── server.py           # FastAPI app (serves HTML + /api/ask)
└── static/
    └── (any local assets if needed)

stitch_mutual_fund_faq_assistant/   # Reference only — do not modify
├── mutual_fund_chatbot_assistant/code.html
├── welcome_faq_assistant_1/code.html
├── welcome_faq_assistant_2/code.html
├── chat_factual_answer_1/code.html
├── chat_factual_answer_2/code.html
├── chat_special_states_1/code.html
├── chat_special_states_2/code.html
├── cognitive_finance_logic_1/DESIGN.md
├── cognitive_finance_logic_2/DESIGN.md
└── mobile_chat_view/code.html
```

### Acceptance Criteria
- [ ] `uvicorn ui.server:app --reload` starts without errors; `http://localhost:8000` loads `index.html`
- [ ] Welcome state (avatar + headline + 3 bento cards) renders correctly on desktop and mobile
- [ ] Clicking an example card populates the input and submits — factual answer bubble appears
- [ ] Sending an advisory query (e.g., *"Should I invest?"*) renders the refusal bubble with the AMFI link
- [ ] Loading skeleton is visible during the API round-trip
- [ ] Source URL in every factual response is a working clickable link
- [ ] Disclaimer banner is visible at all times across all states
- [ ] All 6 correct scheme names appear in the desktop sidebar
- [ ] Mobile view (`< md`) hides the sidebar; hamburger menu is visible
- [ ] `POST /api/ask` returns the correct JSON shape: `{type, answer, source_url, last_updated}` or `{type, message}`

---

## Phase 6: Integration, Testing & Hardening

### Objective
Validate the full end-to-end system, handle edge cases, write a comprehensive README, and ensure the system meets all success criteria from the problem statement.

### Tasks

#### 6.1 — End-to-End Test Suite (`tests/`)
- [ ] Create `tests/test_ingestion.py`:
  - Test scraper returns non-empty HTML for each of 6 URLs
  - Test parser extracts at least one factual field per scheme
  - Test chunker produces chunks within 500-token limit
  - Test upsert idempotency (run twice, verify no duplicates)

- [ ] Create `tests/test_pipeline.py`:
  - Test factual classification for 10 factual queries
  - Test advisory classification for 10 advisory queries
  - Test retriever returns at least 1 result for known factual queries
  - Test LLM response is ≤ 3 sentences
  - Test response always contains `Source:` and `Last updated:` lines

- [ ] Create `tests/test_refusal.py`:
  - Verify refusal response contains AMFI link
  - Verify refusal does not contain any scheme-specific data
  - Verify refusal for: "Should I invest?", "Which fund is better?", "Give me a recommendation"

#### 6.2 — Edge Case Handling
- [ ] Query with no relevant context → graceful fallback message (not a hallucinated answer)
- [ ] Scraper failure (network error) → log error, skip scheme, continue pipeline
- [ ] LLM API timeout → return a user-friendly error message
- [ ] Empty query submission → prompt user to enter a question
- [ ] Very long query (> 500 chars) → truncate before embedding

#### 6.3 — Compliance Checks
- [ ] Manually verify that responses to the following never contain advisory content:
  - "Is ICICI Large Cap a good fund?"
  - "Should I do SIP in Nippon ELSS?"
  - "Which AMC is better?"
- [ ] Verify that PII-adjacent queries ("my portfolio", "my account") trigger graceful responses
- [ ] Verify every factual response has exactly one source URL

#### 6.4 — README (`README.md`)
- [ ] Sections:
  1. **Overview** — what the project does
  2. **Architecture** — brief summary with link to `docs/architecture.md`
  3. **Selected AMCs & Schemes** — table of all 6 schemes
  4. **Setup Instructions** — clone, create venv, install deps, set `.env`, run ingest, run UI
  5. **GitHub Actions Setup** — how to add `GROQ_API_KEY` secret, enable the workflow
  6. **Usage** — how to run the app locally and ask questions
  7. **Known Limitations** — from `architecture.md §9`
  8. **Disclaimer** — *"Facts-only. No investment advice."*

#### 6.5 — Final Review Checklist
- [ ] All 6 scheme pages ingested successfully
- [ ] ChromaDB collection non-empty and queryable
- [ ] Factual queries return accurate, source-backed answers
- [ ] Advisory queries are politely refused
- [ ] GitHub Actions workflow runs successfully on `workflow_dispatch`
- [ ] Streamlit UI loads without errors, disclaimer always visible
- [ ] `.env` is in `.gitignore`; no secrets in codebase
- [ ] `README.md` is complete and setup instructions work from scratch

### Acceptance Criteria (Maps to Problem Statement Success Criteria)

| Success Criterion | Verification Method |
|-------------------|---------------------|
| Accurate retrieval of factual mutual fund information | Manual testing of 20+ factual queries across all 6 schemes |
| Strict adherence to facts-only responses | Advisory query test suite (10 queries) — 100% refusal rate |
| Consistent inclusion of valid source citations | Automated assertion: every factual response contains `Source:` |
| Proper refusal of advisory queries | `tests/test_refusal.py` — all refusals include AMFI link |
| Clean, minimal, and user-friendly interface | Manual UI review; all 6 schemes in sidebar; disclaimer visible |
| Daily corpus refresh | GitHub Actions workflow runs and succeeds on `workflow_dispatch` |

---

## Dependency Graph

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Ingestion Pipeline)
    │
    ├──────────────────────┐
    ▼                      ▼
Phase 3 (RAG Pipeline)   Phase 4 (GitHub Actions Scheduler)
    │
    ▼
Phase 5 (UI)
    │
    ▼
Phase 6 (Integration & Testing)
```

> Phase 4 (Scheduler) depends only on Phase 2 (Ingest script must support `--mode daily`).
> Phases 3 and 4 can be developed in parallel after Phase 2 is complete.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Groww HTML structure changes, breaking parser | Medium | High | Save raw HTML in `data/raw/`; add parser tests; monitor GitHub Actions failures |
| Groq API rate limiting or downtime | Low | High | Add retry logic in `llm_client.py`; return graceful error message |
| ChromaDB upsert overwrites valid data | Low | Medium | Deterministic chunk IDs + pre-upsert validation; 7-day artifact retention for rollback |
| LLM generates advisory content despite system prompt | Low | High | Post-generation advisory keyword check before returning response |
| GitHub Actions free-tier minute limits exceeded | Very Low | Low | Job takes ~2–5 min/day; well within 2,000 min/month limit |
| Scraper blocked by Groww (rate limiting / bot detection) | Medium | High | Add polite delays between requests; rotate User-Agent; implement retry with back-off |

---

## File Creation Checklist

```
# ── Backend & Pipeline ──────────────────────────────────────────
[ ] .github/workflows/daily_ingest.yml
[ ] ingestion/schemes.py
[ ] ingestion/scraper.py
[ ] ingestion/parser.py
[ ] ingestion/chunker.py
[ ] ingestion/embedder.py
[ ] ingestion/ingest.py
[ ] retrieval/chroma_client.py
[ ] retrieval/query_embedder.py
[ ] retrieval/retriever.py
[ ] pipeline/intent_classifier.py
[ ] pipeline/prompt_builder.py
[ ] pipeline/llm_client.py
[ ] pipeline/response_formatter.py
[ ] pipeline/qa_pipeline.py

# ── Frontend UI (assembled from stitch components) ───────────────
[ ] ui/index.html          # Assembled from stitch_mutual_fund_faq_assistant/ components
[ ] ui/app.js              # State machine + Fetch API calls
[ ] ui/server.py           # FastAPI — serves index.html + POST /api/ask

# ── Tests ────────────────────────────────────────────────────────
[ ] tests/test_ingestion.py
[ ] tests/test_pipeline.py
[ ] tests/test_refusal.py

# ── Config & Docs ────────────────────────────────────────────────
[ ] requirements.txt       # Add: fastapi, uvicorn[standard]
[ ] .env.example
[ ] .gitignore
[ ] README.md
```

---

*Implementation Plan for RAG-MF_FAQ | Created: 2026-08-27 | Last Updated: 2026-08-30 | Based on architecture.md & problemStatement.md*

---

## Phase 7: Post-Launch Performance Optimisations (2026-08-30)

### Objective
Investigate and resolve 12–15s response latency and stale NAV data reported after go-live. Implement data freshness and scheduler fixes.

### 7.1 — LLM Model Migration

**File**: `pipeline/llm_client.py`

| | Before | After |
|---|---|---|
| Model | `qwen/qwen3.8-27b` (deprecated Aug 16) | `openai/gpt-oss-20b` |
| Sampling | `temperature=0.1, top_p=0.9` | `temperature=0.1` (top_p removed — redundant) |
| Latency impact | ~8–10s LLM wait | ~1–2s LLM wait |

```python
# pipeline/llm_client.py
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",   # or "openai/gpt-oss-120b" for higher quality
    messages=messages,
    temperature=0.1,
    max_tokens=512,
)
```

### 7.2 — ChromaDB Singleton Cache

**File**: `retrieval/chroma_client.py`

`chromadb.PersistentClient` was being instantiated on **every query**, reopening the SQLite connection each time. Fixed with module-level singleton caching (same pattern as `_model` in `query_embedder.py` and `_client` in `llm_client.py`).

```python
_client = None
_collection = None

def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=persist_directory)
    return _client
```

### 7.3 — Startup Warm-Up

**File**: `ui/server.py`

Added eager pre-loading of the `SentenceTransformer` embedding model and ChromaDB collection at server startup. Previously both were lazy-loaded on the first user request, contributing to first-request latency.

```python
@app.on_event("startup")
def auto_ingest_if_empty():
    # Eager warm-up
    from retrieval.query_embedder import _get_model
    _get_model()  # pre-loads all-MiniLM-L6-v2 into memory
    from retrieval.chroma_client import get_collection
    collection = get_collection()  # opens SQLite connection
```

### 7.4 — In-Memory Query Cache

**File**: `pipeline/qa_pipeline.py`

FAQ bots receive many repeated identical questions. Added a TTL-based in-memory dict cache that bypasses the full embed → retrieve → LLM pipeline for repeated queries.

| Property | Value |
|---|---|
| TTL | 3600s (1 hour) |
| Max entries | 128 (LRU eviction on oldest) |
| Cache key | `" ".join(query.lower().split())` |
| What's cached | Factual answers only |
| Cached latency | < 5ms |

### 7.5 — Stale Data Root Cause & Fix

**File**: `ui/server.py`

**Symptom**: NAV data showed Aug 26 values despite ingestion reporting success on Aug 30.  
**Root Cause**: Both ingest call sites in `server.py` passed `--source processed`, which reads static `.txt` files committed in the repo (`data/processed/*.txt`). These files are one-time reference snapshots, not updated by the scraper.

```diff
# Both startup auto-ingest and /api/ingest/trigger endpoint
- sys.argv = ["ingest.py", "--mode", "daily", "--source", "processed"]
+ sys.argv = ["ingest.py", "--mode", "daily", "--source", "web"]
```

> [!CAUTION]
> Never use `--source processed` in production. The `.txt` files are static and will cause stale data in ChromaDB. Always use `--source web` so Railway scrapes live NAVs from Groww.

### 7.6 — GitHub Actions: Option A → Option B

**File**: `.github/workflows/daily_ingest.yml`

The original Option A workflow ran ingestion inside GitHub Actions and uploaded ChromaDB as an artifact. This artifact was never synced to Railway's persistent volume — making the workflow useless for data freshness.

Replaced with Option B: a lightweight job that calls `POST /api/ingest/trigger` on the live Railway instance, triggering a web scrape directly on the server where ChromaDB persists.

### 7.7 — Ingest Endpoint Security

**File**: `ui/server.py`

- `/api/ingest/trigger`: hardened auth — now always requires `INGEST_API_KEY`; returns `503` if env var not set (previously skipped auth entirely if var was absent)
- `GET /api/ingest/status`: new endpoint to check whether ingestion is currently running (used by GH Actions polling step)

### Acceptance Criteria

- [x] `/api/ask` responds in < 5s for warm requests
- [x] NAV data reflects today's date after manual ingest trigger
- [x] GitHub Actions Option B workflow triggers successfully
- [x] `/api/ingest/trigger` returns 401 on wrong key, 503 if key not set
- [x] Repeated queries return cache hit (< 5ms)
