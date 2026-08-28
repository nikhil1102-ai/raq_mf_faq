# RAG-MF_FAQ

## GitHub Actions Failure Monitoring
The daily ingestion pipeline runs automatically every day at 10:00 UTC.
It uses a GitHub Actions workflow `.github/workflows/daily_ingest.yml`. 

If the ingestion fails for any scheme, the script exits with a non-zero code. This triggers the GitHub Actions workflow to fail. 
Email notifications for failed workflows are enabled by default on the repository owner's account. This serves as our failure monitoring approach.
