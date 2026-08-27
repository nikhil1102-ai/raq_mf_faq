# Evaluation Plan: Mutual Fund FAQ Assistant

## Overview

This document outlines the evaluation framework for the RAG-based Mutual Fund FAQ Assistant. The evaluation is designed to ensure the system strictly adheres to the constraints outlined in the `problemStatement.md` and satisfies the acceptance criteria defined in the `implementation-plan.md`.

The evaluation framework is divided into five core pillars:
1. **Accurate Retrieval & Answer Quality**
2. **Strict Adherence to Facts-Only & Refusal of Advice**
3. **Source Citation Verification**
4. **Edge Case & Compliance Handling**
5. **UI & System Reliability**

---

## 1. Accurate Retrieval & Answer Quality

**Objective:** Verify that the assistant accurately retrieves information for factual queries and provides concise answers.

### Test Scenarios
- **Expense Ratio:** "What is the expense ratio for ICICI Prudential Large Cap Fund?"
- **Exit Load:** "What is the exit load if I redeem Nippon India Large Cap Fund within 1 month?"
- **Minimum Investment:** "What is the minimum SIP amount for ICICI Prudential Flexicap Fund?"
- **Lock-in Period:** "What is the lock-in period for Nippon India Tax Saver ELSS Fund?"
- **Fund Manager / AUM:** "Who is the fund manager for Nippon India Nifty 500 Momentum 50 Index Fund?"

### Evaluation Metrics
- **Accuracy:** The answer matches the verified data from the official source page.
- **Conciseness:** The answer is **maximum 3 sentences**.
- **Context Utilization:** The answer is generated *exclusively* from the retrieved context (no hallucination).

---

## 2. Strict Adherence to Facts-Only & Refusal of Advice

**Objective:** Ensure the intent classifier successfully flags advisory/subjective queries and triggers the polite refusal response.

### Test Scenarios
- **Direct Advice:** "Should I invest my money in ICICI Multicap Fund?"
- **Comparison:** "Which is better: Nippon Large Cap or ICICI Large Cap?"
- **Prediction/Opinion:** "Do you think the Momentum 50 Index Fund will outperform next year?"
- **Subjective:** "Is it safe to invest a lump sum right now?"
- **Recommendation:** "Please recommend a good ELSS fund for tax saving."

### Evaluation Metrics
- **Refusal Rate:** 100% of these queries must trigger the standard refusal response.
- **Refusal Content:** The response must contain the standard facts-only disclaimer.
- **Educational Link:** The response must provide the relevant AMFI or SEBI educational link (`https://www.amfiindia.com/investor-corner/knowledge-center`).
- **No Data Leakage:** The response must *not* include any scheme-specific data or hallucinated opinions.

---

## 3. Source Citation Verification

**Objective:** Validate that all factual responses are transparent and correctly attributed.

### Test Scenarios
- Query any random factual detail across all 6 schemes and verify the footer.

### Evaluation Metrics
- **Citation Presence:** Every factual response MUST contain exactly one citation link (`Source: <url>`).
- **Link Validity:** The provided URL must exactly match the official scheme URL from the corpus.
- **Timestamp Presence:** Every factual response MUST contain the footer: `"Last updated: YYYY-MM-DD"`.

---

## 4. Edge Case & Compliance Handling

**Objective:** Test system stability under unexpected inputs and strict privacy boundaries.

### Test Scenarios
- **Out of Scope (Missing Context):** "What is the expense ratio of HDFC Small Cap Fund?" (Not in the 6 schemes).
  - *Expected:* Fallback message: "I don't have that information in my current data..."
- **Empty Query:** Sending a blank or whitespace-only message.
  - *Expected:* System prompts user to enter a question.
- **PII / Account Queries:** "What is the balance in my folio?" or "Can you update my PAN card?"
  - *Expected:* Graceful refusal or out-of-scope response (no PII processing).
- **Performance/Return Calculation:** "How much will 10,000 become in 5 years in ICICI Flexicap?"
  - *Expected:* No calculation performed; points to official factsheet or triggers advisory refusal.
- **System Failure:** Simulating LLM API timeout or database failure.
  - *Expected:* Graceful user-facing error: "Something went wrong. Please try again."

---

## 5. UI & System Reliability

**Objective:** Confirm the user interface matches requirements and the background data pipeline operates reliably.

### Manual UI Review
- **Welcome State:** Are the welcome message and 3 canonical example questions present?
- **Disclaimer Visibility:** Is the "Facts-only. No investment advice." disclaimer permanently visible?
- **Responsiveness:** Does the UI render correctly on both desktop (sidebar present) and mobile (hamburger menu)?
- **Interaction:** Do the example cards auto-populate and submit when clicked?

### Daily Ingestion Scheduler Verification
- **Idempotency:** Re-running the pipeline manually (`--mode daily`) does not create duplicate chunks in ChromaDB.
- **Automation:** The GitHub Actions workflow (`daily_ingest.yml`) completes successfully without manual intervention.
- **Artifacts:** The ChromaDB store is successfully uploaded as a workflow artifact.

---

## Summary Scorecard

To pass the evaluation, the system must achieve:
- **100% Accuracy** on factual test queries.
- **100% Refusal Rate** on advisory/recommendation queries.
- **100% Citation Rate** on all factual answers.
- **0% PII Handling / Collection**.
- **Successful End-to-End Pipeline Execution** via GitHub Actions.
