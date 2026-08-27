import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ScraperError(Exception):
    pass

def scrape(url: str, slug: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logging.info(f"Scraping {url} (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            html = response.text
            
            with open(f"data/raw/{slug}.html", "w", encoding="utf-8") as f:
                f.write(html)
            return html
        except requests.exceptions.RequestException as e:
            logging.warning(f"Failed to scrape {url}: {e}")
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt
                logging.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                raise ScraperError(f"Failed to scrape {url} after {max_retries} attempts.") from e

if __name__ == "__main__":
    test_url = "https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth"
    try:
        scrape(test_url, "icici_large_cap")
        print("Scraped successfully.")
    except Exception as e:
        print(f"Error: {e}")
