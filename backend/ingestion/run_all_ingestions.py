"""
Master Ingestion Script for MarketVerify.
Runs ingestion for all three distinct RAG vector stores sequentially.
"""
from backend.app.core.logging import logger
from backend.ingestion.ingest_trust_tier import ingest_trust_tier_data
from backend.ingestion.ingest_filings import ingest_filings_data
from backend.ingestion.ingest_sentiment import ingest_sentiment_data


def run_all():
    logger.info("==================================================")
    logger.info("Starting MarketVerify Master Ingestion Pipeline")
    logger.info("==================================================")

    try:
        t_count = ingest_trust_tier_data()
        logger.info(f"Store 1/3 (trust_tier_store): {t_count} records indexed.")
    except Exception as e:
        logger.error(f"Failed ingesting trust_tier_store: {e}")

    try:
        f_count = ingest_filings_data()
        logger.info(f"Store 2/3 (filing_store): {f_count} records indexed.")
    except Exception as e:
        logger.error(f"Failed ingesting filing_store: {e}")

    try:
        s_count = ingest_sentiment_data()
        logger.info(f"Store 3/3 (sentiment_corpus): {s_count} records indexed.")
    except Exception as e:
        logger.error(f"Failed ingesting sentiment_corpus: {e}")

    logger.info("==================================================")
    logger.info("Master Ingestion Completed Successfully!")
    logger.info("==================================================")


if __name__ == "__main__":
    run_all()
