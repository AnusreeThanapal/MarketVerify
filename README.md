# MarketVerify — Multi-Agent Indian Market Rumor Grounding Platform

**MarketVerify** is an institutional market surveillance and rumor verification platform for listed Indian equities (BSE / NSE), built with **FastAPI**, **LangGraph**, **Qdrant**, and **React (Vite + TypeScript)**.

---

## 🏛️ System Architecture

1. **Multi-Agent LangGraph Workflow**:
   - `Ingestion / Normalizer Agent`: Cleans raw text, extracts NSE/BSE tickers, detects English & Tamil (தமிழ்) scripts.
   - `Trust-Tier Agent`: Computes Bayesian Beta credibility priors ($\alpha=2, \beta=2$) from source history.
   - `Verification Agent`: Dual standard ($k=3$) and deep ($k=7$) retrieval against SEBI/BSE regulatory filings, with loop-back retry upon inconclusive evidence.
   - `Sentiment Agent`: Analyzes rumor tone and estimates price lead-lag dynamics.
   - `Aggregator Verdict Agent`: Issues final grounded determination (`CORROBORATED_OFFICIAL`, `CONTRADICTED_BY_FILING`, `UNVERIFIED_RUMOR`, `LIKELY_CREDIBLE`) with full regulatory citations.

2. **Frontend Surveillance Desk**:
   - Built with React + TypeScript + Vite + Tailwind CSS.
   - Distinct routed views via **React Router**:
     - `/verify` — Market Rumor & Claim Verification Docket with pre-configured scenarios.
     - `/claims` — Surveillance Claims Register & Audit Ledger.
     - `/trace/:claimId` — Live Multi-Agent LangGraph Trace with SSE streaming.
     - `/sources` — Source Credibility Docket & Bayesian history.
     - `/data-explorer` — Raw database and Qdrant store inspector (Admin & Auditor only).
   - Official light institutional aesthetic (SEBI/NSE theme) with `Merriweather` serif headings, `Inter` body, and `JetBrains Mono` code.

3. **Role-Based Authentication & Security**:
   - Real PostgreSQL/SQLite `users` table with `bcrypt` password hashes and signed JWT bearer tokens.
   - **Demo Credentials Security**: Plaintext passwords are not shipped in frontend code. Run `python backend/scripts/seed_demo_users.py` to generate `DEMO_CREDENTIALS.local.md` (gitignored), or use the 1-click demo login buttons.

---

## 🚀 Getting Started

### 1. Run Backend Server
```bash
# Start FastAPI backend on dedicated port 8005
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8005
```

### 2. Run Frontend Dev Server
```bash
# In a separate terminal
cd frontend
npm install
npm run dev
```

### 3. Access Portal
- **Surveillance Desk**: [http://localhost:3005](http://localhost:3005)
- **API Docs**: [http://localhost:8005/docs](http://localhost:8005/docs)
