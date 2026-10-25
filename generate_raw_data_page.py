import json
import sqlite3
import html
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "backend", "data")
DB_PATH = os.path.join(BASE_DIR, "marketverify.db")
OUTPUT_PUBLIC_HTML = os.path.join(BASE_DIR, "frontend", "public", "data-explorer", "index.html")
OUTPUT_ROOT_HTML = os.path.join(BASE_DIR, "raw_data_tables.html")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_db_table(table_name):
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute(f"SELECT * FROM {table_name}")
        rows = [dict(r) for r in c.fetchall()]
        return rows
    except Exception as e:
        print(f"Error reading {table_name}: {e}")
        return []
    finally:
        conn.close()

trust_tier = load_json("seed_trust_tier.json")
filings = load_json("seed_filings.json")
sentiment = load_json("seed_sentiment.json")

claims = load_db_table("claims")
verdicts = load_db_table("verdicts")
users = load_db_table("users")

# Mask password hashes
for u in users:
    if "hashed_password" in u:
        u["hashed_password"] = "●●●●●●●● (bcrypt secured)"

# Build claims list with verdicts joined if available
verdict_by_claim = {v.get("claim_id"): v for v in verdicts}
processed_claims = []
for c in claims:
    cid = c.get("id")
    v = verdict_by_claim.get(cid, {})
    raw_ts = c.get("submitted_at") or c.get("created_at")
    if raw_ts and isinstance(raw_ts, str) and not raw_ts.endswith("Z") and "+" not in raw_ts:
        raw_ts = raw_ts.replace(" ", "T") + "Z"
    processed_claims.append({
        "id": cid,
        "raw_text": c.get("raw_text") or c.get("claim_text"),
        "language": c.get("language") or "en",
        "ticker": c.get("ticker"),
        "company_name": c.get("company_name"),
        "source_handle": c.get("source_handle"),
        "submitted_at": raw_ts,
        "status": c.get("status"),
        "verdict_status": v.get("verdict_status"),
        "confidence_score": v.get("confidence_score")
    })

all_data = {
    "trust_tier": trust_tier,
    "filings": filings,
    "sentiment": sentiment,
    "claims": processed_claims,
    "users": users
}

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MarketVerify - Real-Time Live Data Explorer & Institutional Dataset Tables</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --navy-900: #0a192f;
      --navy-800: #0F2744;
      --navy-700: #1B3A6B;
      --navy-600: #2563EB;
      --navy-500: #3B82F6;
      --slate-50: #F8FAFC;
      --slate-100: #F1F5F9;
      --slate-200: #E2E8F0;
      --slate-300: #CBD5E1;
      --slate-500: #64748B;
      --slate-700: #334155;
      --slate-800: #1E293B;
      --slate-900: #0F172A;
      --emerald-600: #059669;
      --emerald-500: #10B981;
      --emerald-50: #ECFDF5;
      --amber-600: #D97706;
      --amber-50: #FFFBEB;
      --rose-600: #E11D48;
      --rose-50: #FFF1F2;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--slate-50);
      color: var(--slate-900);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    header {{
      background: linear-gradient(135deg, var(--navy-900) 0%, var(--navy-800) 50%, var(--navy-700) 100%);
      color: white;
      padding: 1.15rem 2rem;
      border-bottom: 2px solid #2563eb33;
      box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.25);
    }}

    .header-inner {{
      max-width: 1600px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
    }}

    .brand-group {{
      display: flex;
      align-items: center;
      gap: 0.9rem;
    }}

    .badge-institutional {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      font-weight: 600;
      background: rgba(59, 130, 246, 0.2);
      border: 1px solid rgba(147, 197, 253, 0.35);
      color: #93C5FD;
      padding: 0.25rem 0.6rem;
      border-radius: 9999px;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }}

    .live-status-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.72rem;
      font-weight: 600;
      padding: 0.25rem 0.65rem;
      border-radius: 9999px;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #6EE7B7;
    }}

    .pulse-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #10B981;
      box-shadow: 0 0 8px #10B981;
      animation: pulse 2s infinite ease-in-out;
    }}

    @keyframes pulse {{
      0% {{ transform: scale(0.95); opacity: 0.8; }}
      50% {{ transform: scale(1.3); opacity: 1; }}
      100% {{ transform: scale(0.95); opacity: 0.8; }}
    }}

    h1 {{
      font-size: 1.3rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .subtitle {{
      color: #94A3B8;
      font-size: 0.78rem;
      margin-top: 0.15rem;
      font-family: 'JetBrains Mono', monospace;
    }}

    .quick-links {{
      display: flex;
      gap: 0.6rem;
      align-items: center;
    }}

    .btn {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 0.8rem;
      font-weight: 600;
      padding: 0.45rem 0.85rem;
      border-radius: 6px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      cursor: pointer;
      transition: all 0.15s ease;
      border: 1px solid transparent;
    }}

    .btn-secondary {{
      background: rgba(255, 255, 255, 0.1);
      color: #F8FAFC;
      border-color: rgba(255, 255, 255, 0.18);
    }}

    .btn-secondary:hover {{
      background: rgba(255, 255, 255, 0.2);
      color: white;
    }}

    .btn-primary {{
      background: var(--navy-500);
      color: white;
    }}

    .btn-primary:hover {{
      background: var(--navy-600);
    }}

    .btn-sync {{
      background: #059669;
      color: white;
    }}

    .btn-sync:hover {{
      background: #047857;
    }}

    main {{
      max-width: 1600px;
      margin: 1.5rem auto;
      padding: 0 1.5rem;
      flex: 1;
      width: 100%;
    }}

    /* Stats bar */
    .dataset-stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }}

    .stat-card {{
      background: white;
      border: 1px solid var(--slate-200);
      border-radius: 8px;
      padding: 1rem 1.25rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
      cursor: pointer;
      transition: all 0.2s ease;
      position: relative;
    }}

    .stat-card:hover, .stat-card.active {{
      border-color: var(--navy-500);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
    }}

    .stat-card .label {{
      font-size: 0.72rem;
      color: var(--slate-500);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .stat-card .count {{
      font-size: 1.5rem;
      font-weight: 800;
      color: var(--navy-800);
      font-family: 'JetBrains Mono', monospace;
      margin-top: 0.2rem;
    }}

    .stat-card .desc {{
      font-size: 0.72rem;
      color: var(--slate-500);
      margin-top: 0.25rem;
    }}

    .badge-live-pulse {{
      position: absolute;
      top: 0.85rem;
      right: 0.85rem;
      font-size: 0.65rem;
      font-family: 'JetBrains Mono', monospace;
      padding: 0.15rem 0.45rem;
      background: #ECFDF5;
      color: #059669;
      border: 1px solid #A7F3D0;
      border-radius: 4px;
      font-weight: 700;
    }}

    /* Tab navigation */
    .controls-bar {{
      background: white;
      border: 1px solid var(--slate-200);
      border-radius: 8px;
      padding: 0.75rem 1rem;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1rem;
    }}

    .tabs-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
    }}

    .tab-btn {{
      padding: 0.5rem 0.9rem;
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--slate-700);
      background: var(--slate-100);
      border: 1px solid transparent;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}

    .tab-btn:hover {{
      background: var(--slate-200);
    }}

    .tab-btn.active {{
      background: var(--navy-800);
      color: white;
    }}

    .tab-btn .badge-pill {{
      background: rgba(0, 0, 0, 0.15);
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.7rem;
      padding: 0.1rem 0.4rem;
      border-radius: 9999px;
    }}

    .tab-btn.active .badge-pill {{
      background: rgba(255, 255, 255, 0.22);
      color: white;
    }}

    .right-tools {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }}

    .auto-sync-box {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.75rem;
      color: var(--slate-700);
      font-family: 'JetBrains Mono', monospace;
      background: #F8FAFC;
      border: 1px solid var(--slate-300);
      padding: 0.35rem 0.65rem;
      border-radius: 6px;
      cursor: pointer;
    }}

    .filter-group {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      min-width: 280px;
    }}

    .search-box {{
      width: 100%;
      padding: 0.5rem 0.85rem;
      font-size: 0.82rem;
      border: 1px solid var(--slate-300);
      border-radius: 6px;
      outline: none;
      font-family: inherit;
    }}

    .search-box:focus {{
      border-color: var(--navy-500);
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
    }}

    /* Table Container */
    .table-container {{
      background: white;
      border: 1px solid var(--slate-200);
      border-radius: 8px;
      overflow-x: auto;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.82rem;
    }}

    thead {{
      background: var(--slate-100);
      border-bottom: 2px solid var(--slate-200);
      position: sticky;
      top: 0;
      z-index: 10;
    }}

    th {{
      padding: 0.75rem 1rem;
      font-weight: 700;
      color: var(--slate-700);
      text-transform: uppercase;
      font-size: 0.7rem;
      letter-spacing: 0.05em;
      white-space: nowrap;
    }}

    tbody tr {{
      border-bottom: 1px solid var(--slate-200);
      transition: background 0.1s ease;
    }}

    tbody tr:hover {{
      background: #F8FAFC;
    }}

    tbody tr.row-new {{
      animation: highlightRow 3s ease;
    }}

    @keyframes highlightRow {{
      0% {{ background: #DCFCE7; }}
      100% {{ background: transparent; }}
    }}

    td {{
      padding: 0.75rem 1rem;
      color: var(--slate-800);
      vertical-align: top;
      max-width: 450px;
      word-wrap: break-word;
      line-height: 1.45;
    }}

    .code-cell {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      color: var(--navy-700);
      background: #F1F5F9;
      padding: 0.2rem 0.45rem;
      border-radius: 4px;
      display: inline-block;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
      text-transform: uppercase;
    }}

    .badge-true, .badge-positive, .badge-corroborated, .badge-completed, .badge-corroborated_official {{
      background: var(--emerald-50);
      color: var(--emerald-600);
      border: 1px solid #A7F3D0;
    }}

    .badge-false, .badge-negative, .badge-debunked, .badge-contradicted, .badge-failed, .badge-contradicted_official {{
      background: var(--rose-50);
      color: var(--rose-600);
      border: 1px solid #FECDD3;
    }}

    .badge-inconclusive, .badge-neutral, .badge-processing, .badge-no_evidence_found {{
      background: var(--amber-50);
      color: var(--amber-600);
      border: 1px solid #FDE68A;
    }}

    .truncate-text {{
      max-width: 420px;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .link-doc {{
      color: var(--navy-500);
      text-decoration: none;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
    }}

    .link-doc:hover {{
      text-decoration: underline;
    }}

    /* Modal / Inspector */
    .modal-backdrop {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(4px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 1.5rem;
    }}

    .modal-backdrop.open {{
      display: flex;
    }}

    .modal-box {{
      background: white;
      border-radius: 10px;
      width: 100%;
      max-width: 800px;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      border: 1px solid var(--slate-300);
    }}

    .modal-header {{
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--slate-200);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--slate-50);
      border-top-left-radius: 10px;
      border-top-right-radius: 10px;
    }}

    .modal-title {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--navy-800);
      font-family: 'JetBrains Mono', monospace;
    }}

    .close-btn {{
      background: none;
      border: none;
      font-size: 1.25rem;
      cursor: pointer;
      color: var(--slate-500);
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
    }}

    .close-btn:hover {{
      background: var(--slate-200);
      color: var(--slate-900);
    }}

    .modal-body {{
      padding: 1.25rem;
      overflow-y: auto;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
      background: #0B1120;
      color: #E2E8F0;
      line-height: 1.5;
    }}

    .meta-footer {{
      margin-top: 1.5rem;
      padding: 1rem 0 2rem;
      font-size: 0.75rem;
      color: var(--slate-500);
      text-align: center;
      font-family: 'JetBrains Mono', monospace;
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-inner">
      <div class="brand-group">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #60A5FA;">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <path d="m9 12 2 2 4-4"/>
        </svg>
        <div>
          <h1>MarketVerify Raw Data Explorer <span class="badge-institutional">Institutional Audit</span></h1>
          <div class="subtitle">Complete tabular dump of vector knowledge bases, SEBI LODR disclosures & live surveillance ledger</div>
        </div>
      </div>
      <div class="quick-links">
        <div class="live-status-pill">
          <div class="pulse-dot"></div>
          <span id="api-status-text">Backend Connected (:8005)</span>
        </div>
        <button onclick="syncLiveClaims()" class="btn btn-sync" title="Fetch latest submissions from live database">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>
          Sync Live DB
        </button>
        <button onclick="downloadActiveDataset()" class="btn btn-primary">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
          Export Active JSON
        </button>
      </div>
    </div>
  </header>

  <main>
    <!-- Dataset Summary Cards -->
    <div class="dataset-stats">
      <div class="stat-card" onclick="switchTab('claims')" id="card-claims">
        <span class="badge-live-pulse">LIVE SYNC</span>
        <div class="label">Verified Claims (Live SQLite)</div>
        <div class="count" id="count-claims">{len(processed_claims)}</div>
        <div class="desc">Real-time processed claims & verification verdicts</div>
      </div>
      <div class="stat-card" onclick="switchTab('filings')" id="card-filings">
        <div class="label">SEBI LODR Filings (Qdrant)</div>
        <div class="count" id="count-filings">{len(filings)}</div>
        <div class="desc">BSE / NSE corporate disclosures & announcements</div>
      </div>
      <div class="stat-card" onclick="switchTab('trust_tier')" id="card-trust_tier">
        <div class="label">Trust-Tier History (Qdrant)</div>
        <div class="count" id="count-trust_tier">{len(trust_tier)}</div>
        <div class="desc">Historical leak channel accuracy & lag records</div>
      </div>
      <div class="stat-card" onclick="switchTab('sentiment')" id="card-sentiment">
        <div class="label">Sentiment Corpus (Qdrant)</div>
        <div class="count" id="count-sentiment">{len(sentiment)}</div>
        <div class="desc">Multi-lingual market tone & lead-lag patterns</div>
      </div>
      <div class="stat-card" onclick="switchTab('users')" id="card-users">
        <div class="label">Authorized Roles (SQLite)</div>
        <div class="count" id="count-users">{len(users)}</div>
        <div class="desc">RBAC accounts with designated tiers</div>
      </div>
    </div>

    <!-- Controls Bar -->
    <div class="controls-bar">
      <div class="tabs-nav">
        <button class="tab-btn active" onclick="switchTab('claims')" id="tab-btn-claims">
          Claims & Verdicts <span class="badge-pill" id="pill-claims">{len(processed_claims)}</span>
        </button>
        <button class="tab-btn" onclick="switchTab('filings')" id="tab-btn-filings">
          SEBI Filings <span class="badge-pill" id="pill-filings">{len(filings)}</span>
        </button>
        <button class="tab-btn" onclick="switchTab('trust_tier')" id="tab-btn-trust_tier">
          Trust-Tier Sources <span class="badge-pill" id="pill-trust_tier">{len(trust_tier)}</span>
        </button>
        <button class="tab-btn" onclick="switchTab('sentiment')" id="tab-btn-sentiment">
          Sentiment & Lead-Lag <span class="badge-pill" id="pill-sentiment">{len(sentiment)}</span>
        </button>
        <button class="tab-btn" onclick="switchTab('users')" id="tab-btn-users">
          Users & RBAC <span class="badge-pill" id="pill-users">{len(users)}</span>
        </button>
      </div>

      <div class="right-tools">
        <label class="auto-sync-box" title="Periodically queries the live backend every 3 seconds">
          <input type="checkbox" id="auto-sync-checkbox" checked onchange="toggleAutoSync()">
          <span>Auto-Sync Live DB (3s)</span>
        </label>
        <div class="filter-group">
          <input 
            type="text" 
            id="search-input" 
            class="search-box" 
            placeholder="Filter rows by keyword, ticker, headline..."
            oninput="filterRows()"
          />
        </div>
      </div>
    </div>

    <!-- Active Table Viewport -->
    <div class="table-container">
      <table id="data-table">
        <thead id="table-head"></thead>
        <tbody id="table-body"></tbody>
      </table>
    </div>

    <div class="meta-footer">
      Grounding System: MarketVerify • Real-Time Database Bridge: Connected to FastAPI (:8005) & SQLite • Collections: trust_tier_store, filing_store, sentiment_corpus
    </div>
  </main>

  <!-- Detail JSON Inspector Modal -->
  <div class="modal-backdrop" id="json-modal" onclick="closeModal(event)">
    <div class="modal-box" onclick="event.stopPropagation()">
      <div class="modal-header">
        <div class="modal-title" id="modal-title">Raw Document Record</div>
        <button class="close-btn" onclick="closeModal()">&times;</button>
      </div>
      <pre class="modal-body"><code id="modal-content"></code></pre>
    </div>
  </div>

  <script>
    const datasets = {json.dumps(all_data, ensure_ascii=False)};
    let activeTab = 'claims';
    let autoSyncTimer = null;
    let knownClaimIds = new Set(datasets.claims.map(c => c.id));

    const columnsConfig = {{
      claims: [
        {{ key: 'id', label: 'Claim ID', type: 'code' }},
        {{ key: 'ticker', label: 'Ticker', type: 'badge_ticker' }},
        {{ key: 'language', label: 'Lang', type: 'code' }},
        {{ key: 'source_handle', label: 'Source', type: 'code' }},
        {{ key: 'raw_text', label: 'Rumor / Claim Text', type: 'truncate' }},
        {{ key: 'verdict_status', label: 'Verdict', type: 'verdict_badge' }},
        {{ key: 'confidence_score', label: 'Confidence', type: 'confidence' }},
        {{ key: 'status', label: 'Status', type: 'status_badge' }},
        {{ key: 'submitted_at', label: 'Submitted At', type: 'date' }},
        {{ key: '_actions', label: 'Inspect', type: 'action' }}
      ],
      filings: [
        {{ key: 'filing_id', label: 'Filing ID', type: 'code' }},
        {{ key: 'ticker', label: 'Ticker', type: 'badge_ticker' }},
        {{ key: 'company_name', label: 'Company Name' }},
        {{ key: 'filing_type', label: 'Filing Type' }},
        {{ key: 'filing_date', label: 'Date', type: 'code' }},
        {{ key: 'headline', label: 'Headline / Regulatory Subject' }},
        {{ key: 'content_chunk', label: 'SEBI Disclosure Content Chunk', type: 'truncate' }},
        {{ key: 'source_url', label: 'Document Link', type: 'link' }},
        {{ key: '_actions', label: 'Inspect', type: 'action' }}
      ],
      trust_tier: [
        {{ key: 'id', label: 'Record ID', type: 'code' }},
        {{ key: 'source_handle', label: 'Source Handle', type: 'code' }},
        {{ key: 'source_name', label: 'Source Name' }},
        {{ key: 'ticker', label: 'Ticker', type: 'badge_ticker' }},
        {{ key: 'past_claim_text', label: 'Past Rumor / Claim', type: 'truncate' }},
        {{ key: 'was_accurate', label: 'Accurate?', type: 'boolean' }},
        {{ key: 'lag_hours', label: 'Lag (Hrs)', type: 'code' }},
        {{ key: 'category', label: 'Category' }},
        {{ key: 'outcome_summary', label: 'Audited Regulatory Outcome' }},
        {{ key: '_actions', label: 'Inspect', type: 'action' }}
      ],
      sentiment: [
        {{ key: 'id', label: 'Sample ID', type: 'code' }},
        {{ key: 'language', label: 'Lang', type: 'code' }},
        {{ key: 'text_sample', label: 'Market Chatter / Leak Snippet', type: 'truncate' }},
        {{ key: 'sentiment_label', label: 'Polarity', type: 'sentiment_badge' }},
        {{ key: 'tone', label: 'Tone Classification', type: 'code' }},
        {{ key: 'lead_lag_behavior', label: 'Lead-Lag Market Behavior' }},
        {{ key: '_actions', label: 'Inspect', type: 'action' }}
      ],
      users: [
        {{ key: 'id', label: 'User ID', type: 'code' }},
        {{ key: 'email', label: 'Email', type: 'code' }},
        {{ key: 'role', label: 'Institutional Role', type: 'code' }},
        {{ key: 'is_active', label: 'Active', type: 'boolean' }},
        {{ key: 'hashed_password', label: 'Password Protection', type: 'code' }},
        {{ key: '_actions', label: 'Inspect', type: 'action' }}
      ]
    }};

    // Live Sync Function to poll FastAPI backend
    async function syncLiveClaims() {{
      const apiStatusEl = document.getElementById('api-status-text');
      try {{
        const response = await fetch('http://127.0.0.1:8005/api/v1/claims?page=1&page_size=100');
        if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
        const result = await response.json();
        const liveItems = result.items || [];

        if (Array.isArray(liveItems) && liveItems.length > 0) {{
          let hasNew = false;
          // Format live items into dataset structure
          const formatted = liveItems.map(item => {{
            if (!knownClaimIds.has(item.id)) {{
              hasNew = true;
              knownClaimIds.add(item.id);
            }}
            return {{
              id: item.id,
              raw_text: item.raw_text,
              language: item.language,
              ticker: item.ticker,
              company_name: item.company_name,
              source_handle: item.source_handle,
              submitted_at: item.submitted_at,
              status: item.status,
              verdict_status: item.verdict_status,
              confidence_score: item.confidence_score,
              isNew: hasNew
            }};
          }});

          datasets.claims = formatted;
          document.getElementById('count-claims').innerText = formatted.length;
          document.getElementById('pill-claims').innerText = formatted.length;

          if (apiStatusEl) {{
            apiStatusEl.innerText = `Live Connected (${{formatted.length}} claims synced)`;
            apiStatusEl.parentElement.style.borderColor = 'rgba(16, 185, 129, 0.4)';
          }}

          if (activeTab === 'claims') {{
            renderTable();
          }}
        }}
      }} catch (err) {{
        console.warn("Live API sync check:", err.message);
        if (apiStatusEl) {{
          apiStatusEl.innerText = "API Standby / Reconnecting...";
          apiStatusEl.parentElement.style.borderColor = 'rgba(234, 179, 8, 0.4)';
        }}
      }}
    }}

    function toggleAutoSync() {{
      const enabled = document.getElementById('auto-sync-checkbox').checked;
      if (enabled) {{
        if (!autoSyncTimer) {{
          autoSyncTimer = setInterval(syncLiveClaims, 3000);
        }}
      }} else {{
        if (autoSyncTimer) {{
          clearInterval(autoSyncTimer);
          autoSyncTimer = null;
        }}
      }}
    }}

    function switchTab(tabKey) {{
      activeTab = tabKey;
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      const activeBtn = document.getElementById('tab-btn-' + tabKey);
      if (activeBtn) activeBtn.classList.add('active');

      document.querySelectorAll('.stat-card').forEach(c => c.classList.remove('active'));
      const activeCard = document.getElementById('card-' + tabKey);
      if (activeCard) activeCard.classList.add('active');

      document.getElementById('search-input').value = '';
      renderTable();
    }}

    function renderTable() {{
      const config = columnsConfig[activeTab] || [];
      const query = (document.getElementById('search-input').value || '').trim().toLowerCase();
      let rows = datasets[activeTab] || [];

      if (query) {{
        rows = rows.filter(row => {{
          return Object.values(row).some(v => String(v || '').toLowerCase().includes(query));
        }});
      }}

      // Render Header
      const thead = document.getElementById('table-head');
      thead.innerHTML = `<tr>${{config.map(c => `<th>${{c.label}}</th>`).join('')}}</tr>`;

      // Render Body
      const tbody = document.getElementById('table-body');
      if (rows.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="${{config.length}}" style="text-align: center; padding: 3rem; color: #64748B;">No records matched your search query.</td></tr>`;
        return;
      }}

      tbody.innerHTML = rows.map((row, idx) => {{
        const rowClass = row.isNew ? 'row-new' : '';
        return `<tr class="${{rowClass}}">${{config.map(col => renderCell(row, col, idx)).join('')}}</tr>`;
      }}).join('');
    }}

    function renderCell(row, col, idx) {{
      if (col.type === 'action') {{
        return `<td><button class="btn btn-secondary" style="padding: 0.2rem 0.5rem; font-size: 0.72rem;" onclick="viewRawRow(${{idx}})">JSON</button></td>`;
      }}

      const val = row[col.key];
      if (val === undefined || val === null || val === '') {{
        return `<td style="color: #94A3B8;">—</td>`;
      }}

      if (col.type === 'code') {{
        return `<td><span class="code-cell">${{escapeHtml(String(val))}}</span></td>`;
      }}

      if (col.type === 'badge_ticker') {{
        return `<td><span class="code-cell" style="font-weight: 700; color: #1B3A6B; background: #DBEAFE; border: 1px solid #BFDBFE;">${{escapeHtml(String(val))}}</span></td>`;
      }}

      if (col.type === 'boolean') {{
        const isTrue = Boolean(val);
        return `<td><span class="badge badge-${{isTrue ? 'true' : 'false'}}">${{isTrue ? 'YES' : 'NO'}}</span></td>`;
      }}

      if (col.type === 'status_badge') {{
        const s = String(val).toLowerCase();
        return `<td><span class="badge badge-${{s}}">${{escapeHtml(String(val))}}</span></td>`;
      }}

      if (col.type === 'verdict_badge') {{
        const s = String(val).toLowerCase();
        let cls = 'neutral';
        if (s.includes('corroborated')) cls = 'corroborated';
        else if (s.includes('contradicted')) cls = 'contradicted';
        else if (s.includes('no_evidence') || s.includes('inconclusive')) cls = 'inconclusive';
        return `<td><span class="badge badge-${{cls}}">${{escapeHtml(String(val).replace(/_/g, ' '))}}</span></td>`;
      }}

      if (col.type === 'confidence') {{
        const num = parseFloat(val);
        const pct = isNaN(num) ? '' : Math.round(num * 100) + '%';
        return `<td><span class="code-cell" style="font-weight: 700;">${{pct || escapeHtml(String(val))}}</span></td>`;
      }}

      if (col.type === 'sentiment_badge') {{
        const s = String(val).toUpperCase();
        let cls = 'neutral';
        if (s.includes('POS')) cls = 'positive';
        if (s.includes('NEG')) cls = 'negative';
        return `<td><span class="badge badge-${{cls}}">${{escapeHtml(s)}}</span></td>`;
      }}

      if (col.type === 'truncate') {{
        return `<td><div class="truncate-text" title="${{escapeHtml(String(val))}}">${{escapeHtml(String(val))}}</div></td>`;
      }}

      if (col.type === 'date') {{
        let displayStr = String(val);
        try {{
          let dateStr = String(val).trim();
          if (!dateStr.endsWith('Z') && !dateStr.includes('+')) {{
            dateStr = dateStr.replace(' ', 'T') + 'Z';
          }}
          const d = new Date(dateStr);
          if (!isNaN(d.getTime())) {{
            displayStr = d.toLocaleString(undefined, {{
              year: 'numeric',
              month: 'short',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
              hour12: true
            }});
          }}
        }} catch (e) {{
          displayStr = String(val).replace('T', ' ').substring(0, 19);
        }}
        return `<td><span class="code-cell" style="font-weight: 600;" title="ISO: ${{escapeHtml(String(val))}}">${{escapeHtml(displayStr)}}</span></td>`;
      }}

      if (col.type === 'link') {{
        return `<td><a href="${{val}}" target="_blank" rel="noopener noreferrer" class="link-doc">PDF / Filing <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg></a></td>`;
      }}

      return `<td>${{escapeHtml(String(val))}}</td>`;
    }}

    function filterRows() {{
      renderTable();
    }}

    function viewRawRow(idx) {{
      const query = (document.getElementById('search-input').value || '').trim().toLowerCase();
      let rows = datasets[activeTab] || [];
      if (query) {{
        rows = rows.filter(row => Object.values(row).some(v => String(v || '').toLowerCase().includes(query)));
      }}
      const record = rows[idx];
      if (!record) return;

      document.getElementById('modal-title').innerText = `${{activeTab.toUpperCase()}} Record #${{idx + 1}}`;
      document.getElementById('modal-content').innerText = JSON.stringify(record, null, 2);
      document.getElementById('json-modal').classList.add('open');
    }}

    function closeModal(e) {{
      document.getElementById('json-modal').classList.remove('open');
    }}

    function downloadActiveDataset() {{
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(datasets[activeTab], null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", `marketverify_${{activeTab}}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    }}

    function escapeHtml(str) {{
      return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }}

    // Initial render and start auto-sync
    switchTab('claims');
    syncLiveClaims();
    autoSyncTimer = setInterval(syncLiveClaims, 3000);
  </script>
</body>
</html>
"""

# Write to both frontend public directory and root directory
with open(OUTPUT_PUBLIC_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

with open(OUTPUT_ROOT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Successfully generated connected live data pages at:\n  1. {OUTPUT_PUBLIC_HTML}\n  2. {OUTPUT_ROOT_HTML}")
