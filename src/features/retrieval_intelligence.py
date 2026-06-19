from __future__ import annotations
from typing import Dict, Any


def compute_retrieval_intelligence(features: Dict[str, Any]) -> Dict[str, float]:
    retrieval_expertise = float(features.get("retrieval_expertise", 0.0) or 0.0)
    retrieval_depth = float(features.get("retrieval_depth", 0.0) or 0.0)
    retrieval_maturity = float(features.get("retrieval_maturity", 0.0) or 0.0)
    retrieval_specialist_probability = float(features.get("retrieval_specialist_probability", 0.0) or 0.0)
    retrieval_impact = float(features.get("retrieval_impact", 0.0) or 0.0)

    intelligence = (
        0.30 * retrieval_expertise +
        0.20 * retrieval_depth +
        0.20 * retrieval_maturity +
        0.15 * retrieval_specialist_probability +
        0.15 * retrieval_impact
    )
    intelligence = max(0.0, min(1.0, intelligence))

    return {
        "retrieval_intelligence": intelligence,
    }
