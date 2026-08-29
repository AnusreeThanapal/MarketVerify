# MarketVerify Backend

**MarketVerify** is a multi-agent, retrieval-grounded rumor verification backend engineered specifically for the Indian stock market (NSE / BSE). It validates market claims and social rumors in English and Tamil against official regulatory filings, historical source credibility trajectories, and market sentiment dynamics using **LangGraph** for multi-agent workflow orchestration.

---

## Architecture Overview

```
                      +-----------------------------+
                      |   POST /api/v1/claims       |
                      |   (English / Tamil Claims)  |
                      +--------------+--------------+
                                     |
                                     v
                 +---------------------------------------+
                 |       LangGraph Orchestrator          |
                 +-------------------+-------------------+
                                     |
                                     v
                 +---------------------------------------+
                 | 1. Ingestion / Normalizer Agent       |
                 | - Language detection (en / ta)        |
                 | - Entity extraction (RELIANCE, INFY)  |
                 +-------------------+-------------------+
                                     |
                                     v
+------------------------+  +---------------------------------------+
|   trust_tier_store     |->| 2. Trust-Tier Agent                   |
|   (Historical Records) |  | - Computes Source Trust Score (0-1)   |
+------------------------+  +-------------------+-------------------+
                                                |
                                    [Trust Score <= 0.40?]
                                    /                   \
                        (Yes: DEEP Search)       (No: Standard Search)
                                  \                       /
                                   v                     v
+------------------------+  +---------------------------------------+
|      filing_store      |->| 3. Verification Agent                 |
|  (SEBI / BSE Filings)  |  | - CORROBORATED / CONTRADICTED / NONE  |
+------------------------+  +-------------------+-------------------+
                                                |
                                    [Inconclusive & Retry Count == 0?]
                                    /                                \
                             (Yes: Loop-back)                  (No: Continue)
                                  /                                    \
                         (Query Expansion)                              v
                                  \                 +---------------------------------------+
+------------------------+         +--------------->| 4. Sentiment Agent                    |
|    sentiment_corpus    |------------------------->| - POSITIVE / NEGATIVE / NEUTRAL       |
|  (Tone & Lead-Lag DB)  |                          | - Lead-Lag Price Timing Dynamic       |
+------------------------+                          +-------------------+-------------------+
                                                                        |
                                                                        v
                                                    +---------------------------------------+
                                                    | 5. Aggregator / Verdict Agent         |
                                                    | - Multi-factor synthesis              |
                                                    | - Final Verdict & Confidence Score    |
                                                    +-------------------+-------------------+
                                                                        |
                                                                        v
                                                    +---------------------------------------+
                                                    | Structured Result + Execution Trace   |
                                                    | (Stored in Postgres, Streamed Redis)  |
                                                    +---------------------------------------+
```

---

## The Three Distinct RAG Stores

Market rumors cannot be reliably verified with a single generic vector collection because **evidence types require fundamentally different schemas, retrieval parameters, and semantic roles**:

| Store Name | Collection Purpose | Payload Structure | Retrieval Role & Configuration |
| :--- | :--- | :--- | :--- |
| **`trust_tier_store`** | Evaluates author credibility over time. | `source_handle`, `past_claim_text`, `was_accurate`, `lag_hours`, `category`, `outcome_summary`, `outcome_date` | Evaluates the **source**, not the claim. Computes a calibrated Bayesian trust score ($0.0 - 1.0$). |
| **`filing_store`** | Verifies claim facts against official exchange disclosures. | `ticker`, `company_name`, `filing_type` (SEBI Reg 30, Board Outcome, Press Release), `filing_date`, `headline`, `content_chunk`, `source_url` | Evaluates **claim corroboration / contradiction**. Supports standard ($k=3$, threshold=0.65) vs deep ($k=7$, threshold=0.45) retrieval and query expansion. |
| **`sentiment_corpus`** | Grounds tone and market psychological reaction. | `text_sample`, `language` (en, ta), `sentiment_label` (POSITIVE, NEGATIVE, NEUTRAL), `tone`, `lead_lag_behavior` | Classifies **market tone and price lead-lag dynamics** (e.g. whether rumors of this type move price before or after filing). |

---

## The 5 Single-Responsibility Agent Nodes

1. **`IngestionNormalizerAgent`**:
   - Takes raw claim text (English or Tamil) and source handle.
   - Detects language via Unicode inspection.
   - Normalizes text and extracts stock tickers (`RELIANCE`, `TATASTEEL`, `INFY`, `HDFCBANK`, `ZOMATO`, `PAYTM`, etc.) and company aliases.
2. **`TrustTierAgent`**:
   - Retrieves historical claims and actual outcomes for the source from `trust_tier_store`.
   - Computes Bayesian trust score and confidence level with cited trajectory records.
3. **`VerificationAgent`**:
   - Queries `filing_store` for regulatory disclosures matching the company and claim.
   - Implements dual-retrieval configs: standard vs deep search (when flagged by low source trust).
   - Generates structured citations (`filing_type`, `filing_date`, `headline`, `similarity_score`, `snippet`, `source_url`).
4. **`SentimentAgent`**:
   - Queries `sentiment_corpus` for matching English/Tamil examples.
   - Assigns sentiment label and synthesizes a lead-lag dynamic note.
5. **`AggregatorVerdictAgent`**:
   - Synthesizes all three evidence streams into a final verdict enum:
     - `CORROBORATED_OFFICIAL`
     - `LIKELY_CREDIBLE`
     - `UNVERIFIED_RUMOR`
     - `CONTRADICTED_BY_FILING`
     - `DEBUNKED_FALSEHOOD`
     - `NO_EVIDENCE_FOUND`
   - Computes overall confidence score and a decision-grade rationale.

---

## LangGraph Orchestration & Routing Logic

- **State Representation**: `AgentState` TypedDict maintaining input parameters, agent outputs, retrieval previews, and an ordered `trace: List[TraceEntry]`.
- **Low-Trust Routing**: If `trust_score <= 0.40` or confidence is `LOW`, the graph sets `deep_retrieval_flag = True`, causing the Verification Agent to use a wider top-k ($k=7$) and relaxed threshold ($0.45$).
- **Loop-Back Retry**: If the first verification pass yields `NO_EVIDENCE_FOUND` and `verification_pass_count < 2`, the graph loops back to the Verification Agent with an **expanded query** (adding corporate action synonyms and exchange keywords).
- **Execution Trace**: Every node records `{agent, step_index, input_summary, retrieved_doc_ids, retrieved_docs_preview, output_summary, metadata, timestamp}`.

---

## Local Setup & Quickstart

### Prerequisites
- Docker & Docker Compose
- Python 3.11+

### 1. Start Infrastructure with Docker Compose
Start PostgreSQL 16, Qdrant Vector DB, and Redis 7:

```bash
docker-compose up -d postgres qdrant redis
```

### 2. Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Run Ingestion for all 3 RAG Stores
Populate Qdrant vector collections with realistic seed data:

```bash
python backend/ingestion/run_all_ingestions.py
```

### 4. Run Alembic Database Migrations
```bash
alembic upgrade head
```

### 5. Start the FastAPI Application
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI documentation is available at: `http://localhost:8000/docs`.

---

## Running the Automated Test Suite

Run the full Pytest test suite with asyncio support:

```bash
pytest backend/tests -v --tb=short
```

---

## API Usage Examples

### 1. Submit an English Market Claim
```bash
curl -X POST "http://localhost:8000/api/v1/claims" \
     -H "Content-Type: application/json" \
     -d '{
       "raw_text": "Reliance Retail is in talks to acquire 40% stake in quick commerce app Zepto.",
       "source_handle": "@dalalstreetinsider",
       "ticker": "RELIANCE"
     }'
```

### 2. Submit a Tamil Market Claim
```bash
curl -X POST "http://localhost:8000/api/v1/claims" \
     -H "Content-Type: application/json" \
     -d '{
       "raw_text": "டாடா ஸ்டீல் 1:10 பங்கு பிரிப்பு அறிவிக்க உள்ளதாக தகவல்",
       "source_handle": "@tamil_market_guru"
     }'
```

### 3. Fetch Claim Verdict and Execution Trace
```bash
curl -X GET "http://localhost:8000/api/v1/claims/<CLAIM_ID>"
```

### 4. Retrieve Source Trust History
```bash
curl -X GET "http://localhost:8000/api/v1/sources/@dalalstreetinsider/trust-history"
```

### 5. Health Check
```bash
curl -X GET "http://localhost:8000/health"
```
