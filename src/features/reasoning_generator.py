from __future__ import annotations
from typing import Dict, Any


def generate_reasoning(candidate: Dict[str, Any], rank: int, final_score: float) -> str:
    title = candidate.get("profile_title") or "Unknown"
    years = candidate.get("years_of_experience", 0.0) or 0.0
    skills_count = candidate.get("retrieval_specialist_signal_count", 0) or 0

    ev = candidate.get("evidence_score", 0.0) or 0.0
    jd_cov = candidate.get("jd_coverage", 0.0) or 0.0
    alignment = (ev + jd_cov) / 2.0
    if alignment >= 0.6:
        quality = "strong resume-job alignment"
    elif alignment >= 0.3:
        quality = "moderate resume-job alignment"
    else:
        quality = "basic resume-job alignment"

    return f"{title} with {years} yrs; {skills_count} AI core skills; {quality}."
