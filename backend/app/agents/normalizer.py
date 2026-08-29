import re
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional, List
from backend.app.agents.state import AgentState
from backend.app.core.logging import logger

# Indian Listed Companies Entity Dictionary (English & Tamil mappings)
KNOWN_COMPANIES = [
    {
        "ticker": "RELIANCE",
        "name": "Reliance Industries Limited",
        "aliases": ["reliance", "ril", "jio", "reliance retail", "ரிலையன்ஸ்", "ஜியோ"],
    },
    {
        "ticker": "TATASTEEL",
        "name": "Tata Steel Limited",
        "aliases": ["tata steel", "tatasteel", "tata", "டாடா ஸ்டீல்", "டாடா"],
    },
    {
        "ticker": "INFY",
        "name": "Infosys Limited",
        "aliases": ["infosys", "infy", "இன்ஃபோசிஸ்"],
    },
    {
        "ticker": "HDFCBANK",
        "name": "HDFC Bank Limited",
        "aliases": ["hdfc bank", "hdfc", "hdfcbank", "ஹெச்டிஎஃப்சி"],
    },
    {
        "ticker": "TCS",
        "name": "Tata Consultancy Services Limited",
        "aliases": ["tcs", "tata consultancy"],
    },
    {
        "ticker": "ZOMATO",
        "name": "Zomato Limited",
        "aliases": ["zomato", "blinkit", "ஸோமாட்டோ"],
    },
    {
        "ticker": "ADANIENT",
        "name": "Adani Enterprises Limited",
        "aliases": ["adani enterprises", "adani", "அதானி"],
    },
    {
        "ticker": "WIPRO",
        "name": "Wipro Limited",
        "aliases": ["wipro", "விப்ரோ"],
    },
    {
        "ticker": "ITC",
        "name": "ITC Limited",
        "aliases": ["itc", "itc limited"],
    },
    {
        "ticker": "PAYTM",
        "name": "One97 Communications Limited",
        "aliases": ["paytm", "one97", "பேடிஎம்"],
    },
    {
        "ticker": "TITAN",
        "name": "Titan Company Limited",
        "aliases": ["titan", "caratlane", "டைட்டன்"],
    },
    {
        "ticker": "BAJFINANCE",
        "name": "Bajaj Finance Limited",
        "aliases": ["bajaj finance", "bajfinance", "பஜாஜ் பைனான்ஸ்"],
    },
    {
        "ticker": "TATAMOTORS",
        "name": "Tata Motors Limited",
        "aliases": ["tata motors", "tatamotors", "டாடா மோட்டார்ஸ்"],
    },
    {
        "ticker": "SBIN",
        "name": "State Bank of India",
        "aliases": ["sbi", "sbin", "state bank of india"],
    },
]


class IngestionNormalizerAgent:
    """
    Normalizes raw text, detects language (English / Tamil),
    and extracts Indian equity tickers and company names.
    """

    def __init__(self):
        self.name = "IngestionNormalizerAgent"

    def detect_language(self, text: str) -> str:
        # Check for Tamil Unicode block U+0B80 - U+0BFF
        tamil_chars = re.findall(r"[\u0B80-\u0BFF]", text)
        if len(tamil_chars) > 3:
            return "ta"
        return "en"

    def extract_entities(self, text: str) -> Tuple[Optional[str], Optional[str], List[str]]:
        lower_text = text.lower()
        extracted_entities = []
        found_ticker = None
        found_name = None

        for item in KNOWN_COMPANIES:
            for alias in item["aliases"]:
                # Word boundary search or unicode substring
                pattern = r"(?:^|\b|\s)" + re.escape(alias) + r"(?:$|\b|\s)"
                if re.search(pattern, lower_text) or alias in lower_text:
                    if not found_ticker:
                        found_ticker = item["ticker"]
                        found_name = item["name"]
                    extracted_entities.append(alias)
                    break

        return found_ticker, found_name, extracted_entities

    def normalize_text(self, text: str) -> str:
        # Clean extra whitespace, standardize formatting
        cleaned = re.sub(r"\s+", " ", text).strip()
        return cleaned

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        raw_text = state.get("raw_text", "")
        lang_override = state.get("language")
        
        detected_lang = lang_override if lang_override in ["en", "ta"] else self.detect_language(raw_text)
        normalized = self.normalize_text(raw_text)
        
        ticker = state.get("ticker")
        company_name = state.get("company_name")
        
        if not ticker:
            extracted_ticker, extracted_name, entities = self.extract_entities(normalized)
            ticker = extracted_ticker
            company_name = extracted_name
        else:
            entities = [ticker]

        trace_entry = {
            "agent": self.name,
            "step_index": len(state.get("trace", [])) + 1,
            "input_summary": f"Raw text: '{raw_text[:80]}...' | Source: {state.get('source_handle')}",
            "retrieved_doc_ids": [],
            "retrieved_docs_preview": [],
            "output_summary": f"Language: {detected_lang} | Ticker: {ticker or 'UNKNOWN'} | Company: {company_name or 'UNKNOWN'} | Entities: {entities}",
            "metadata": {
                "detected_language": detected_lang,
                "extracted_ticker": ticker,
                "extracted_company": company_name,
                "entities_found": entities,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        trace_list = list(state.get("trace", []))
        trace_list.append(trace_entry)

        logger.info(f"[{self.name}] Processed claim. Ticker={ticker}, Lang={detected_lang}")

        return {
            "language": detected_lang,
            "normalized_text": normalized,
            "ticker": ticker,
            "company_name": company_name,
            "extracted_entities": entities,
            "trace": trace_list,
        }
