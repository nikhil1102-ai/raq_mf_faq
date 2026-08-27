from bs4 import BeautifulSoup
import re
import os

def parse(html: str, scheme: dict) -> str:
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove navigation, headers, footers and scripts
    for element in soup(["script", "style", "nav", "header", "footer"]):
        element.extract()
        
    # Extract specific target sections by looking for keywords and getting their parent containers
    keywords = [
        "Expense ratio", "Exit load", "Min. for SIP", "Fund size", "NAV:", 
        "Rating", "Risk", "Benchmark", "Lock-in", "Fund Manager"
    ]
    
    extracted_facts = set()
    
    # Also grab the main text, but focusing on the tables/divs that contain facts
    for k in keywords:
        elems = soup.find_all(string=re.compile(k, re.I))
        for elem in elems:
            parent = elem.parent
            for _ in range(2):
                if parent and parent.parent:
                    parent = parent.parent
            if parent:
                text = parent.get_text(separator=" : ", strip=True)
                if len(text) < 500:  # Avoid capturing the whole page if structure is weird
                    extracted_facts.add(text)
    
    # Combine with some generic page text just in case (e.g. descriptions)
    # Get all text from paragraph tags
    paragraphs = soup.find_all("p")
    for p in paragraphs:
        text = p.get_text(separator=" ", strip=True)
        if text:
            extracted_facts.add(text)
            
    cleaned_text = "\n\n".join(list(extracted_facts))
    
    header = f"[Scheme: {scheme['name']} | AMC: {scheme['amc']} | Category: {scheme['category']} | Source: {scheme['url']}]\n\n"
    final_text = header + cleaned_text
    
    os.makedirs("data/processed", exist_ok=True)
    with open(f"data/processed/{scheme['slug']}.txt", "w", encoding="utf-8") as f:
        f.write(final_text)
        
    return final_text
