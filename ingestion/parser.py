"""
Parser module for extracting structured factual data from Groww mutual fund HTML pages.

Extracts:
- NAV, date
- Min SIP, Min Lump Sum
- Fund Size (AUM)
- Expense Ratio
- Rating (Groww stars)
- Exit Load (current policy)
- Stamp Duty
- Tax Implications (STCG/LTCG)
- Benchmark Index
- Risk Level (Riskometer)
- Lock-in Period (ELSS)
- Fund Manager
- Fund Description / Investment Objective
"""

from bs4 import BeautifulSoup
import re
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Generic Groww UI tooltip definitions — these are NOT scheme-specific facts
BOILERPLATE_PATTERNS = [
    "A fee payable to a mutual fund house",
    "A percentage of your capital gains payable",
    "A form of tax payable for the purchase",
    "Taxation is categorized as long-term capital gains",
    "Understand terms",
    "Check past data",
    "Mutual Fund Houses",
    "Mutual Funds screener",
    "Filter funds based on risk",
    "Know about AMCs",
    "Average of the yearly returns",
    "The total return of a mutual fund",
    "NFO",
    "Start SIP",
    "Build long-term wealth",
]


def _is_boilerplate(text: str) -> bool:
    """Check if text is a generic Groww tooltip/definition (not scheme-specific)."""
    for pattern in BOILERPLATE_PATTERNS:
        if pattern.lower() in text.lower():
            return True
    return False


def _extract_fund_details(soup: BeautifulSoup) -> dict:
    """Extract key-value pairs from the fund details container (NAV, SIP, AUM, etc.)."""
    facts = {}
    container = soup.find("div", class_=re.compile(r"fundDetails_fundDetailsContainer"))
    if not container:
        return facts

    detail_divs = container.find_all("div", class_=re.compile(r"fundDetails_gap4"))
    for div in detail_divs:
        children = div.find_all(recursive=False)
        texts = [c.get_text(strip=True) for c in children]
        if len(texts) >= 2:
            key = texts[0].strip()
            value = texts[1].strip()
            if key and value:
                facts[key] = value
        elif len(texts) == 1:
            # Single value like Rating stars — check for star rating
            text = texts[0]
            if text.isdigit():
                facts["Rating"] = text
    return facts


def _extract_investment_objective(soup: BeautifulSoup) -> str:
    """Extract the fund description and investment objective."""
    obj_div = soup.find("div", class_=re.compile(r"investmentObjective"))
    if not obj_div:
        return ""

    text = obj_div.get_text(separator=" ", strip=True)
    # Clean up — remove the "About ..." prefix if present
    text = re.sub(r"^About\s+", "", text)
    # Remove trailing "Scheme Information Document(SID)" and similar
    text = re.sub(r"\s*Scheme Information Document\(SID\)\s*$", "", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_exit_load(soup: BeautifulSoup) -> dict:
    """Extract exit load, stamp duty, and tax information."""
    facts = {}
    section = soup.find("div", class_=re.compile(r"exitLoadStampDutyTax"))
    if not section:
        return facts

    text = section.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Parse exit load — look for the current (first dated) entry
    exit_load_lines = []
    in_exit_load = False
    for i, line in enumerate(lines):
        if line == "Exit Load":
            in_exit_load = True
            continue
        if in_exit_load:
            # First entry after "Exit Load" heading is the current policy
            if re.match(r"\d{2}\s\w+\s\d{4}", line):
                # Date line — next line should be the actual exit load text
                if i + 1 < len(lines):
                    exit_load_lines.append(lines[i + 1])
                break
            elif line.startswith("Exit load") or line == "--" or line == "Nil":
                exit_load_lines.append(line)
                break

    if exit_load_lines:
        load_text = exit_load_lines[0]
        if load_text == "--":
            load_text = "Nil"
        facts["Exit Load"] = load_text

    # Parse stamp duty — look for the percentage value, not the tooltip
    in_stamp_duty = False
    for i, line in enumerate(lines):
        if "Stamp duty on investment" in line:
            in_stamp_duty = True
            continue
        if in_stamp_duty:
            # The value line contains a percentage like "0.005% (from July 1st, 2020)"
            if "%" in line:
                facts["Stamp Duty"] = line.strip()
                break
            in_stamp_duty = False

    # Parse tax implication
    for i, line in enumerate(lines):
        if "Tax implication" in line and i + 1 < len(lines):
            facts["Tax Implication"] = lines[i + 1]
            break

    return facts


def _extract_benchmark(soup: BeautifulSoup) -> str:
    """Extract the fund benchmark index."""
    for elem in soup.find_all(string=re.compile(r"Fund benchmark", re.I)):
        parent = elem.parent
        if parent and parent.parent:
            parent = parent.parent
        text = parent.get_text(separator=" | ", strip=True)
        # Extract just the benchmark name
        match = re.search(r"Fund benchmark\s*\|\s*(.+?)(\s*\||\s*$)", text)
        if match:
            return match.group(1).strip()
        # Fallback: take text after "Fund benchmark"
        parts = text.split("Fund benchmark")
        if len(parts) > 1:
            benchmark = parts[1].strip().lstrip(":").strip()
            # Remove trailing junk
            benchmark = re.sub(r"\s*\|.*$", "", benchmark)
            return benchmark
    return ""


def _extract_risk_level(soup: BeautifulSoup) -> str:
    """Extract the riskometer classification."""
    header = soup.find("header")
    if header:
        risk_elems = header.find_all(string=re.compile(r"(Very High|High|Moderately High|Moderate|Low)\s*Risk", re.I))
        for r in risk_elems:
            return r.strip()
    # Fallback: search entire page
    risk_elems = soup.find_all(string=re.compile(r"(Very High|High|Moderately High|Moderate|Low)\s*Risk", re.I))
    for r in risk_elems:
        return r.strip()
    return ""


def _extract_lock_in(soup: BeautifulSoup) -> str:
    """Extract lock-in period (relevant for ELSS funds)."""
    for elem in soup.find_all(string=re.compile(r"lock.in", re.I)):
        text = elem.strip()
        # Look for patterns like "3Y Lock-in" or "ELSS • 3Y Lock-in"
        match = re.search(r"(\d+[YyMm])\s*Lock.in", text, re.I)
        if match:
            return match.group(1) + " Lock-in"
    return ""


def _extract_fund_manager(soup: BeautifulSoup) -> str:
    """Extract the fund manager name from the investment objective section."""
    obj_div = soup.find("div", class_=re.compile(r"investmentObjective"))
    if obj_div:
        text = obj_div.get_text(separator=" ", strip=True)
        # Pattern: "X is the Current Fund Manager of ..."
        match = re.search(r"([A-Z][a-zA-Z'\. ]+?)\s+is the Current Fund Manager", text)
        if match:
            return match.group(1).strip()
        # Pattern: "Current Fund Manager of ... fund is X"
        match = re.search(r"Current Fund Manager[s]?\s+of\s+.+?\s+(?:fund\s+)?is\s+([A-Z][a-zA-Z'\. ]+?)(?:\.|,|\s+fund)", text, re.I)
        if match:
            return match.group(1).strip()
    return ""


def parse(html: str, scheme: dict) -> str:
    """
    Parse raw HTML from a Groww mutual fund page and extract structured facts.
    
    Returns a clean, structured text document with the scheme metadata header
    and all extracted facts organized into semantic groups.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts, styles, nav, etc.
    for element in soup(["script", "style", "nav", "noscript", "link", "meta"]):
        element.decompose()

    # Extract all facts
    fund_details = _extract_fund_details(soup)
    objective_text = _extract_investment_objective(soup)
    exit_load_info = _extract_exit_load(soup)
    benchmark = _extract_benchmark(soup)
    risk_level = _extract_risk_level(soup)
    lock_in = _extract_lock_in(soup)
    fund_manager = _extract_fund_manager(soup)

    # Build structured output
    sections = []

    # Header (always present)
    header = (
        f"[Scheme: {scheme['name']} | AMC: {scheme['amc']} | "
        f"Category: {scheme['category']} | Source: {scheme['url']}]"
    )
    sections.append(header)

    # Section 1: Key Fund Details
    details_lines = []
    nav_key = next((k for k in fund_details if k.startswith("NAV")), None)
    if nav_key:
        details_lines.append(f"{nav_key}: {fund_details[nav_key]}")
    if "Fund size (AUM)" in fund_details:
        details_lines.append(f"Fund Size (AUM): {fund_details['Fund size (AUM)']}")
    if "Expense ratio" in fund_details:
        details_lines.append(f"Expense Ratio: {fund_details['Expense ratio']}")
    if "Min. for SIP" in fund_details:
        details_lines.append(f"Minimum SIP: {fund_details['Min. for SIP']}")
    if "Rating" in fund_details:
        details_lines.append(f"Groww Rating: {fund_details['Rating']} stars")
    if risk_level:
        details_lines.append(f"Risk Level: {risk_level}")
    if benchmark:
        details_lines.append(f"Benchmark: {benchmark}")
    if lock_in:
        details_lines.append(f"Lock-in Period: {lock_in}")
    if fund_manager:
        details_lines.append(f"Fund Manager: {fund_manager}")

    if details_lines:
        sections.append("Key Fund Details:\n" + "\n".join(details_lines))

    # Section 2: Exit Load, Stamp Duty, Tax
    policy_lines = []
    if "Exit Load" in exit_load_info:
        policy_lines.append(f"Exit Load: {exit_load_info['Exit Load']}")
    if "Stamp Duty" in exit_load_info:
        policy_lines.append(f"Stamp Duty: {exit_load_info['Stamp Duty']}")
    if "Tax Implication" in exit_load_info:
        policy_lines.append(f"Tax Implication: {exit_load_info['Tax Implication']}")

    if policy_lines:
        sections.append("Exit Load, Stamp Duty & Tax:\n" + "\n".join(policy_lines))

    # Section 3: Fund Description / Investment Objective
    if objective_text:
        # Clean out facts already captured above to reduce redundancy
        sections.append(f"Fund Description:\n{objective_text}")

    # Join sections with double newlines
    final_text = "\n\n".join(sections)

    # Save to data/processed/
    os.makedirs("data/processed", exist_ok=True)
    output_path = os.path.join("data", "processed", f"{scheme['slug']}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    logging.info(f"Parsed {scheme['slug']}: {len(final_text)} chars, {len(sections)} sections")
    return final_text
