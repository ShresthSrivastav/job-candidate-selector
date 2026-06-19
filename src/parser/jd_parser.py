from __future__ import annotations
import re
from typing import Dict, List
from src.utils.logger import debug


DEFAULT_RETRIEVAL = [
    "faiss",
    "pinecone",
    "qdrant",
    "milvus",
    "weaviate",
    "elastic",
    "opensearch",
    "bm25",
]

DEFAULT_RANKING = ["ndcg", "ltr", "mrr", "map", "ranking", "recommendation"]
DEFAULT_ML = ["rag", "fine-tuning", "transformers", "embeddings", "llm", "prompt"]
DEFAULT_PRODUCT = ["saas", "shipped", "launched", "production", "a/b test", "ab test"]


class JDParser:
    def __init__(self):
        self.word_re = re.compile(r"[a-zA-Z0-9\-\+]+")

    def parse(self, jd_text: str) -> Dict[str, List[str]]:
        text = jd_text.lower()
        tokens = set(self.word_re.findall(text))

        # must-have heuristics
        must_have = set()
        good_to_have = set()

        # simple rules: if 'must have' present, capture nearby tokens (simple split)
        if "must have" in text or "required" in text:
            # fallback: add high-signal tokens as must
            for term in ["retrieval", "ranking", "search", "ndcg", "python", "evaluation"]:
                if term in text:
                    must_have.add(term)

        # populate groups from defaults if mentioned
        retrieval_reqs = [t for t in DEFAULT_RETRIEVAL if t in text or t in tokens]
        ranking_reqs = [t for t in DEFAULT_RANKING if t in text or t in tokens]
        ml_reqs = [t for t in DEFAULT_ML if t in text or t in tokens]
        product_reqs = [t for t in DEFAULT_PRODUCT if t in text or t in tokens]

        # everything that looks like a tech token and isn't in must -> good
        for tok in tokens:
            if tok in ("and", "or", "with", "the", "a", "an", "in", "on"):
                continue
            # basic filter for short garbage
            if len(tok) <= 1:
                continue
            # treat high-signal tokens as must
            if tok in {"retrieval", "ranking", "search", "ndcg", "pinecone", "faiss"}:
                must_have.add(tok)
            else:
                good_to_have.add(tok)

        result = {
            "must_have": sorted(list(must_have)),
            "good_to_have": sorted(list(good_to_have)),
            "retrieval_reqs": retrieval_reqs,
            "ranking_reqs": ranking_reqs,
            "ml_reqs": ml_reqs,
            "product_reqs": product_reqs,
            "total_requirements": len(must_have) + len(good_to_have),
        }

        debug("Parsed JD requirements: must={}, good={} ", result["must_have"], result["good_to_have"])
        return result
