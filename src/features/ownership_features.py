from __future__ import annotations
import re
from typing import Dict, Any, Set

_OWNERSHIP_VERBS_RE = re.compile(
    r"\b(led|architected|owned|drove|spearheaded|founded|created|established|built from scratch)\b",
    re.IGNORECASE,
)

_SENIORITY_TITLES: Set[str] = {
    "principal", "staff", "lead", "senior", "head of",
    "director", "vp", "vice president", "chief", "cto",
}

_SCALE_RE = re.compile(
    r"\b(millions?\s*(?:of\s*)?(?:users|customers|requests|queries)|"
    r"\d+\s*(?:million|billion|thousand)\s*(?:users|customers|requests|queries)|"
    r"high.?throughput|low.?latency|real.?time|"
    r"(?:revenue|budget)\s*(?:impact|responsible|managed|owned)|"
    r"ab\s*test|a/b\s*test|experiment|rolled\s*out|"
    r"cross.?functional|team\s*lead|managed|mentored)\b",
    re.IGNORECASE,
)

_SCALE_WEIGHTS = {"millions": 5.0, "large_number": 5.0, "perf": 3.0,
                  "revenue": 3.0, "experiment": 2.0, "leadership": 2.0}


def compute_ownership_score(normalized_candidate: Dict[str, Any]) -> Dict[str, float]:
    career_text = str(normalized_candidate.get("career_text", "") or "")
    title = str(normalized_candidate.get("profile_title", "") or "").lower()

    verb_count = len(_OWNERSHIP_VERBS_RE.findall(career_text))
    has_seniority = any(t in title for t in _SENIORITY_TITLES)
    scale_matches = len(_SCALE_RE.findall(career_text))

    raw = (min(verb_count / 3.0, 1.0) * 0.4 +
           (1.0 if has_seniority else 0.0) * 0.3 +
           min(scale_matches / 4.0, 1.0) * 0.3)
    ownership_score = max(0.0, min(1.0, raw))

    return {
        "ownership_score": ownership_score,
        "ownership_verb_count": verb_count,
        "ownership_has_seniority": has_seniority,
        "ownership_scale_score": float(scale_matches),
    }
