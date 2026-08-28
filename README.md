# RAG-MF FAQ Assistant

A full-stack RAG (Retrieval-Augmented Generation) application designed to provide factual answers to frequently asked questions about Mutual Funds, powered by official data sourced from Groww.

## Scope
The assistant currently supports **6 Mutual Fund schemes** across 2 AMCs (ICICI Prudential and Nippon India):
- ICICI Prudential Large Cap Fund
- ICICI Prudential Flexicap Fund
- ICICI Prudential Multicap Fund
- Nippon India Nifty 500 Momentum 50 Index Fund
- Nippon India Large Cap Fund
- Nippon India Tax Saver ELSS Fund

For a full list of sources, see [docs/sources.md](docs/sources.md).
For a list of sample questions and responses, see [docs/sample_qa.md](docs/sample_qa.md).

## Setup Steps

### 1. Backend (FastAPI + ChromaDB) - Deployed on Railway
1. **Clone the repository.**
2. Set up a Railway project and link your GitHub repository.
3. Configure the following Environment Variables in Railway:
   - `GROQ_API_KEY`: Your Groq API key for LLM generation.
   - `FRONTEND_URL`: The URL of your Vercel frontend (to configure CORS).
4. **Data Ingestion:**
   The backend automatically seeds ChromaDB on the first startup if the database is empty. You can also manually trigger ingestion using the `python ingestion/ingest.py` script.

### 2. Frontend (HTML/JS) - Deployed on Vercel
1. Set up a Vercel project and link the repository.
2. The `vercel.json` file configures Vercel to serve the `ui/` directory.
3. The frontend directly calls the Railway API backend to prevent serverless function timeouts.

## Known Limits
- **Data Freshness:** Data is ingested daily via GitHub Actions. Real-time intraday NAV or market data is not supported.
- **Strict Factual Guardrails:** The assistant intentionally refuses to answer advisory questions (e.g., "Which fund is best?") and personal data queries (e.g., PAN/Aadhar balances).
- **Vercel Timeout Restrictions:** To circumvent Vercel's Hobby plan 30-second proxy timeout, the frontend communicates directly with the Railway backend via CORS.
- **LLM Rate Limits:** Dependent on the Groq API limits (Llama 3 8B model).

## GitHub Actions Failure Monitoring
The daily ingestion pipeline runs automatically every day at 10:00 UTC using a GitHub Actions workflow `.github/workflows/daily_ingest.yml`. 

If the ingestion fails for any scheme, the script exits with a non-zero code. This triggers the GitHub Actions workflow to fail. Email notifications for failed workflows are enabled by default on the repository owner's account. This serves as our failure monitoring approach.
