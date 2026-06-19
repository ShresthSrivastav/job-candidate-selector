from __future__ import annotations
from typing import Dict, Any
from src.utils.logger import debug
from src.models.candidate import Candidate


TECH_TITLE_KEYWORDS = [
    "senior",
    "lead",
    "principal",
    "ml",
    "ai",
    "engineer",
    "search",
    "recommendation",
    "research",
]


def normalize_candidate(record: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a raw candidate record into canonical pipeline structure."""
    # Use Pydantic v2 API if available to avoid deprecation warnings.
    cand = None
    try:
        # model_validate exists in Pydantic v2
        validate = getattr(Candidate, "model_validate", None)
        if callable(validate):
            cand = Candidate.model_validate(record)
        else:
            # fallback to v1 parse_obj
            cand = Candidate.parse_obj(record)
    except Exception as e:
        debug("Pydantic parse failed, attempting best-effort normalization: {}", e)
        cand = None

    # candidate_id
    candidate_id = record.get("candidate_id") if isinstance(record, dict) else None

    # profile
    profile = record.get("profile") if isinstance(record, dict) else {}
    headline = None
    summary = None
    years_of_experience = None
    current_title = None
    if profile:
        headline = profile.get("headline")
        summary = profile.get("summary")
        years_of_experience = profile.get("years_of_experience")
        current_title = profile.get("current_title")

    # skills
    skills = []
    raw_skills = record.get("skills") if isinstance(record, dict) else []
    if raw_skills:
        for s in raw_skills:
            name = None
            try:
                # skill may be dict
                if isinstance(s, dict):
                    name = s.get("name")
                else:
                    name = str(s)
            except Exception:
                continue
            if name:
                skills.append(name.strip().lower())

    # career text
    career_text_parts = []
    if summary:
        career_text_parts.append(summary.lower())
    if headline:
        career_text_parts.append(headline.lower())
    career_history = record.get("career_history") if isinstance(record, dict) else []
    if career_history:
        for item in career_history:
            desc = item.get("description") if isinstance(item, dict) else None
            if desc:
                career_text_parts.append(desc.lower())

    career_text = " \n ".join(career_text_parts)

    # title bonus
    title_bonus = 0.0
    title_str = (current_title or "")
    title_lower = title_str.lower() if isinstance(title_str, str) else ""
    for kw in TECH_TITLE_KEYWORDS:
        if kw in title_lower:
            title_bonus = 0.1
            break

    normalized = {
        "candidate_id": candidate_id,
        "profile_title": current_title or headline,
        "years_of_experience": float(years_of_experience) if years_of_experience is not None else 0.0,
        "skills_names": skills,
        "career_text": career_text,
        "title_bonus": title_bonus,
        "raw_json": record,
    }

    return normalized
