# MarketVerify — Official Indian Market Rumor Verification Portal

**MarketVerify** is an official, retrieval-grounded market surveillance and rumor verification platform for Indian equities (BSE / NSE), built with an institutional light design system evoking the authoritative trust of regulatory bodies (SEBI / NSE / RBI).

---

## 🔐 Authentication & Surveillance Roles

The platform features a **database-backed authentication system** (PostgreSQL/SQLite + bcrypt password hashing + signed JWTs with role claims).

### 1-Click Demo Login
To ensure maximum security and avoid shipping plaintext passwords in the frontend client, demo login buttons authenticate securely via `POST /api/v1/auth/demo-login`.

To inspect or generate local demo credentials:
```bash
python backend/scripts/seed_demo_users.py
```
This writes `DEMO_CREDENTIALS.local.md` to your repository root (gitignored for safety).

| Surveillance Role | Oversight Scope |
| :--- | :--- |
| **Surveillance Analyst** | Submit market claims, inspect live multi-agent traces, view verified citations and dashboard ledger. |
| **Chief Compliance Officer** | Analyst capabilities plus source credibility surveillance and compliance review docket. |
| **Platform Administrator** | Full access plus system configuration and **Data Explorer** for raw Postgres and Qdrant store inspection. |
| **Regulatory Auditor** | Strict read-only oversight: inspect verdicts, audit agent traces, and review raw data stores (mutation buttons omitted). |

---

## 🏛️ Visual Design System & Navigation

- **Navigation Architecture**: Full React Router architecture with distinct routes:
  - `/verify` — Market Rumor & Claim Verification Docket with pre-configured scenarios.
  - `/claims` — Surveillance Claims Register & Audit Ledger with ticker filters and search.
  - `/trace/:claimId` — Live Multi-Agent LangGraph Trace with SSE streaming.
  - `/sources` — Source Credibility Docket & Bayesian history.
  - `/data-explorer` — Raw database and Qdrant vector store inspector (Admin & Auditor only).
- **Institutional Light Theme**: Paper canvas (`#F7F8FA`) with crisp 1px bordered report cards (`#D8DEE8`), avoiding generic SaaS templates.
- **Authority Palette**: Deep Institutional Navy (`#0F2744` / `#1B3A6B`) for masthead, primary actions, and section headers.
- **Tricolor Hairline Accent**: Restrained Saffron (`#E06A14`) and Green (`#137547`) hairline strip symbolizing Indian market authority.
- **Official Typography**: `Merriweather` serif for headers, `Inter` sans-serif for body/data, and `JetBrains Mono` for tickers, timestamps, and regulatory IDs.

---

## 🚀 Local Development Setup

```bash
# 1. Start backend server (port 8005)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8005

# 2. Start frontend dev server (port 3005)
cd frontend
npm install
npm run dev
```

Open **[http://localhost:3005](http://localhost:3005)** in your browser.
