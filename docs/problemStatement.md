# Problem Statement: Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Overview

The objective of this project is to build a **facts-only FAQ assistant** for mutual fund schemes, using **Groww** as the reference product context. The assistant will answer objective, verifiable queries related to mutual funds by retrieving information exclusively from official public sources, such as AMC (Asset Management Company) websites, AMFI, and SEBI.

The system must strictly **avoid providing investment advice, opinions, or recommendations**. Every response must include a single, clear source link and adhere to defined constraints around clarity, accuracy, and compliance.

---

## Objective

Design and implement a lightweight **Retrieval-Augmented Generation (RAG)**-based assistant that:

- Answers factual queries about mutual fund schemes
- Uses a curated corpus of official documents
- Provides concise, source-backed responses

---

## Target Users

- Retail investors comparing mutual fund schemes
- Customer support and content teams handling repetitive mutual fund queries

---

## Scope of Work

### 1. Corpus Definition

Select **two Asset Management Companies (AMCs)** with **three mutual fund schemes from each**, ensuring category diversity (e.g., large-cap, flexi-cap, ELSS).

#### AMC-1: ICICI Prudential Mutual Fund

| # | Scheme Name | Source Link |
|---|-------------|-------------|
| 1 | ICICI Prudential Large Cap Fund – Direct Growth | [Groww Link](https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth) |
| 2 | ICICI Prudential Flexicap Fund – Direct Growth | [Groww Link](https://groww.in/mutual-funds/icici-prudential-flexicap-fund-direct-growth) |
| 3 | ICICI Prudential Multicap Fund – Direct Growth | [Groww Link](https://groww.in/mutual-funds/icici-prudential-multicap-fund-direct-growth) |

#### AMC-2: Nippon India Mutual Fund

| # | Scheme Name | Source Link |
|---|-------------|-------------|
| 4 | Nippon India Nifty 500 Momentum 50 Index Fund – Direct Growth | [Groww Link](https://groww.in/mutual-funds/nippon-india-nifty-500-momentum-50-index-fund-direct-growth) |
| 5 | Nippon India Large Cap Fund – Direct Growth | [Groww Link](https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth) |
| 6 | Nippon India Tax Saver ELSS Fund – Direct Growth | [Groww Link](https://groww.in/mutual-funds/nippon-india-elss-tax-saver-fund-direct-growth) |

---

### 2. FAQ Assistant Requirements

The assistant must answer **facts-only** queries, such as:

- Expense ratio of a scheme
- Exit load details
- Minimum SIP amount
- ELSS lock-in period
- Riskometer classification
- Benchmark index
- Process to download statements or capital gains reports

**Each response must:**

- Be limited to a **maximum of 3 sentences**
- Include **exactly one citation link**
- Include the following footer:
  > *"Last updated from sources: `<date>`"*

---

### 3. Refusal Handling

The assistant must **refuse non-factual or advisory queries**, such as:

- *"Should I invest in this fund?"*
- *"Which fund is better?"*

Refusal responses should:

- Be polite and clearly worded
- Reinforce the facts-only limitation
- Provide a relevant educational link (e.g., AMFI or SEBI resource)

---

### 4. User Interface (Minimal)

The solution should include a simple interface with:

- A **welcome message**
- **Three example questions**
- A visible disclaimer:
  > *"Facts-only. No investment advice."*

---

## Constraints

### Data and Sources
- Use only **official public sources** (Groww links shared for each scheme)
- Do **not** use third-party blogs or aggregator websites

### Privacy and Security
Do **not** collect, store, or process:
- PAN or Aadhaar numbers
- Account numbers
- OTPs
- Email addresses or phone numbers

### Content Restrictions
- No investment advice or recommendations
- No performance comparisons or return calculations
- For performance-related queries, provide a link to the **official factsheet only**

### Transparency
- Responses must be short, factual, and verifiable
- Every answer must include a **source link** and **last updated date**

---

## Expected Deliverables

### README Document
- Setup instructions
- Selected AMC and schemes
- Architecture overview (RAG approach)
- **LLM:** Groq `qwen3.6-27b`
- **Vector DB:** ChromaDB
- Known limitations

### Disclaimer Snippet
> *"Facts-only. No investment advice."*

---

## Success Criteria

| Criterion | Description |
|-----------|-------------|
| Accurate Retrieval | Accurate retrieval of factual mutual fund information |
| Facts-Only Responses | Strict adherence to facts-only responses |
| Source Citations | Consistent inclusion of valid source citations |
| Advisory Refusal | Proper refusal of advisory queries |
| Clean UI | Clean, minimal, and user-friendly interface |

---

## Summary

The goal is to build a **trustworthy, transparent, and compliant** mutual fund FAQ assistant that prioritizes **accuracy over intelligence**. The system should ensure that users receive only verified, source-backed financial information, without any advisory bias or speculative content.
