from __future__ import annotations
from typing import Dict, Any, List


def compute_eligibility(
    normalized_candidate: Dict[str, Any],
    jd_requirements: Dict[str, List[str]],
    retrieval_skills: List[str],
    jd_text: str = "",
) -> Dict[str, float]:
    skills = set(normalized_candidate.get("skills_names", []))
    career_text = normalized_candidate.get("career_text", "") or ""
    title = (normalized_candidate.get("profile_title") or "").lower()
    years = float(normalized_candidate.get("years_of_experience", 0.0) or 0.0)

    musts = set(jd_requirements.get("must_have", []))
    goods = set(jd_requirements.get("good_to_have", []))
    matched_must = sum(1 for m in musts if m in skills or m in career_text)
    matched_good = sum(1 for g in goods if g in skills or g in career_text)
    denom = max(4 * len(musts) + 1 * len(goods), 1)
    jd_coverage = (4 * matched_must + 1 * matched_good) / denom

    years_fit = max(0.0, 1.0 - abs(years - 7.0) / 7.0)

    retrieval_skill_presence = 0.0
    if retrieval_skills:
        count = sum(1 for r in retrieval_skills if r in skills or r in career_text)
        retrieval_skill_presence = min(count / 5.0, 1.0)

    retrieval_titles = {"search engineer", "retrieval engineer", "recommendation engineer",
                        "search", "retrieval", "ranking engineer", "nlp engineer"}
    title_match = 1.0 if any(t in title for t in retrieval_titles) else 0.0

    eligibility = (
        0.40 * jd_coverage +
        0.30 * years_fit +
        0.20 * retrieval_skill_presence +
        0.10 * title_match
    )
    eligibility = max(0.0, min(1.0, eligibility))

    return {
        "eligibility_score": eligibility,
        "eligibility_jd_coverage": jd_coverage,
        "eligibility_years_fit": years_fit,
        "eligibility_retrieval_presence": retrieval_skill_presence,
        "eligibility_title_match": title_match,
    }
