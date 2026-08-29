import hashlib
import re
from typing import List, Optional
import numpy as np
from backend.app.config import get_settings
from backend.app.core.logging import logger

settings = get_settings()


class EmbeddingService:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate a normalized dense vector embedding.
        Uses deterministic semantic projection based on tokens, n-grams, and keywords,
        ensuring repeatable vector retrieval for testing and offline execution.
        """
        if not text:
            return [0.0] * self.dimension

        cleaned = text.lower().strip()
        words = re.findall(r"[\w\u0B80-\u0BFF]+", cleaned)  # Supports English and Tamil unicode
        
        vec = np.zeros(self.dimension, dtype=np.float32)

        # 1. Word level projection
        for i, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            pos = h % self.dimension
            weight = 1.0 / (1.0 + 0.1 * i)
            vec[pos] += weight * (1.0 if (h % 2 == 0) else -0.5)

            # Character trigrams for morphological and cross-lingual robustness
            for j in range(max(0, len(word) - 2)):
                tri = word[j : j + 3]
                tri_h = int(hashlib.sha256(tri.encode("utf-8")).hexdigest(), 16)
                tri_pos = tri_h % self.dimension
                vec[tri_pos] += 0.35 * (1.0 if (tri_h % 2 == 0) else -0.35)

        # 2. Key entity amplification (tickers, financial keywords)
        special_keywords = {
            "reliance": 10, "zepto": 11, "tatasteel": 12, "tata": 12, "infy": 13, "infosys": 13,
            "hdfc": 14, "hdfcbank": 14, "zomato": 15, "adani": 16, "adanient": 16, "wipro": 17,
            "itc": 18, "paytm": 19, "tcs": 20, "titan": 21, "caratlane": 22, "bajaj": 23,
            "acquire": 30, "stake": 31, "split": 32, "resigns": 33, "capex": 34, "contract": 35,
            "denial": 36, "clarification": 37, "approval": 38,
            # Tamil keywords
            "ரிலையன்ஸ்": 10, "டாடா": 12, "இன்ஃபோசிஸ்": 13, "ஹெச்டிஎஃப்சி": 14, "பங்கு": 32, "ஒப்பந்தம்": 35,
        }
        for kw, idx in special_keywords.items():
            if kw in cleaned:
                bucket = (idx * 17) % self.dimension
                vec[bucket] += 2.5

        # Normalize to unit length for Cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            vec[0] = 1.0

        return vec.tolist()

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(t) for t in texts]


embedding_service = EmbeddingService(dimension=settings.EMBEDDING_DIMENSION)

def get_embedding_service() -> EmbeddingService:
    return embedding_service
