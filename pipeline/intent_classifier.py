import logging
from typing import Literal

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

ADVISORY_PATTERNS = [
    "should i", "which is better", "recommend", "advice",
    "opinion", "worth investing", "good fund", "compare returns",
    "outperform", "best fund", "suggest", "is it safe to invest",
    "better than", "which fund", "worth it", "good investment"
]

PERSONAL_PATTERNS = [
    "pan", "aadhar", "folio", "portfolio", "my investment", "my account"
]

def classify(query: str) -> Literal["FACTUAL", "ADVISORY", "PERSONAL"]:
    query_lower = query.lower()
    
    # Check for personal data intent first
    for pattern in PERSONAL_PATTERNS:
        if pattern in query_lower:
            logging.info(f"Query classified as PERSONAL (matched: '{pattern}')")
            return "PERSONAL"
            
    # Then check for advisory intent
    for pattern in ADVISORY_PATTERNS:
        if pattern in query_lower:
            logging.info(f"Query classified as ADVISORY (matched: '{pattern}')")
            return "ADVISORY"
            
    logging.info("Query classified as FACTUAL")
    return "FACTUAL"

def refusal_response() -> str:
    return (
        "I can only provide factual information about mutual fund schemes.\n"
        "For investment guidance, please consult a SEBI-registered advisor or\n"
        "visit AMFI's investor education portal: https://www.amfiindia.com/investor"
    )

def personal_data_response() -> str:
    return ( 
	   "I don't have access to personal investment or portfolio data linked to your PAN/Aadhar or folio number.\n"
	   "To check your holdings, please visit your registrar's portal or the official AMC website."
	)
