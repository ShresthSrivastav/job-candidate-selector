from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime


def _years_from_career(career_history: List[Dict[str, Any]]) -> float:
    months = 0
    for item in career_history or []:
        dm = item.get("duration_months")
        try:
            months += int(dm or 0)
        except Exception:
            continue
    return months / 12.0


def profile_completeness(normalized_candidate: Dict[str, Any]) -> float:
    raw = normalized_candidate.get("raw_json", {}) or {}
    profile = raw.get("profile") or {}
    required = [
        "anonymized_name", "headline", "summary", "location",
        "country", "years_of_experience", "current_title",
        "current_company", "current_company_size", "current_industry",
    ]
    present = sum(1 for k in required if profile.get(k) not in (None, "", []))
    return present / len(required)


def career_consistency(normalized_candidate: Dict[str, Any]) -> float:
    raw = normalized_candidate.get("raw_json", {}) or {}
    profile = raw.get("profile") or {}
    claimed_years = float(profile.get("years_of_experience") or 0.0)
    ch = raw.get("career_history") or []
    yrs = _years_from_career(ch)
    if claimed_years <= 0 and yrs <= 0:
        return 0.0
    if claimed_years <= 0:
        return 0.0
    diff = abs(claimed_years - yrs)
    score = max(0.0, 1.0 - diff / max(claimed_years, yrs, 1.0))
    return float(score)


def engagement_score(normalized_candidate: Dict[str, Any]) -> float:
    raw = normalized_candidate.get("raw_json", {}) or {}
    signals = raw.get("redrob_signals") or {}
    if not signals:
        return 0.0
    pcs = float(signals.get("profile_completeness_score") or 0.0) / 100.0
    views = float(signals.get("profile_views_received_30d") or 0.0)
    endorsements = float(signals.get("endorsements_received") or 0.0)
    score = min(1.0, pcs * 0.6 + min(1.0, views / 100.0) * 0.2 + min(1.0, endorsements / 20.0) * 0.2)
    return float(score)


def compute_quality_v2(normalized_candidate: Dict[str, Any]) -> Dict[str, Any]:
    profile_score = profile_completeness(normalized_candidate)
    career_score = career_consistency(normalized_candidate)
    engage = engagement_score(normalized_candidate)

    quality = (
        0.40 * profile_score +
        0.35 * career_score +
        0.25 * engage
    )

    return {
        "profile_completeness": float(profile_score),
        "career_consistency": float(career_score),
        "engagement_score": float(engage),
        "candidate_quality_v2": float(quality),
    }
