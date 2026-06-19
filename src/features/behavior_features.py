from __future__ import annotations
from typing import Dict, Any
from datetime import datetime


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _days_since_date(date_str: str) -> float:
    if not date_str:
        return float("inf")
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            d = datetime.strptime(date_str.split("+")[0], fmt)
            delta = datetime.utcnow() - d
            return float(delta.days)
        except Exception:
            continue
    return float("inf")


def compute_behavioral_features(normalized_candidate: Dict[str, Any]) -> Dict[str, Any]:
    raw = normalized_candidate.get("raw_json", {}) or {}
    signals = raw.get("redrob_signals") or {}

    open_to_work = bool(signals.get("open_to_work_flag") or signals.get("open_to_work") or False)

    recruiter_response_rate = _safe_float(signals.get("recruiter_response_rate"), 0.0)
    interview_completion_rate = _safe_float(signals.get("interview_completion_rate"), 0.0)

    profile_views = _safe_float(signals.get("profile_views_received_30d") or signals.get("profile_views"), 0.0)
    search_appearances = _safe_float(signals.get("search_appearance_30d") or signals.get("search_appearances"), 0.0)
    saved_by_recruiters = _safe_float(signals.get("saved_by_recruiters_30d") or signals.get("saved_by_recruiters"), 0.0)

    last_active_days = signals.get("last_active_days")
    if last_active_days is None:
        lad = signals.get("last_active_date")
        if lad:
            last_active_days = _days_since_date(lad)
    try:
        last_active_days = float(last_active_days) if last_active_days is not None else float("inf")
    except Exception:
        last_active_days = float("inf")

    notice_period_days = signals.get("notice_period_days")
    try:
        notice_period_days = float(notice_period_days) if notice_period_days is not None else None
    except Exception:
        notice_period_days = None

    pv_norm = min(1.0, profile_views / 100.0) if profile_views >= 0 else 0.0
    sa_norm = min(1.0, search_appearances / 100.0) if search_appearances >= 0 else 0.0
    saved_norm = min(1.0, saved_by_recruiters / 10.0) if saved_by_recruiters >= 0 else 0.0
    rr_norm = min(1.0, max(0.0, recruiter_response_rate))
    icr_norm = min(1.0, max(0.0, interview_completion_rate))
    last_active_norm = 0.0
    if last_active_days is not None and last_active_days != float("inf"):
        last_active_norm = max(0.0, 1.0 - min(last_active_days / 30.0, 1.0))

    notice_norm = 0.5
    if notice_period_days is None:
        notice_norm = 0.5
    else:
        notice_norm = max(0.0, 1.0 - min(notice_period_days, 90.0) / 90.0)

    weights = {
        "open_to_work": 0.18,
        "recruiter_response_rate": 0.15,
        "interview_completion_rate": 0.15,
        "search_appearances": 0.12,
        "saved_by_recruiters": 0.10,
        "profile_views": 0.10,
        "last_active": 0.20,
    }

    behavior_super_score = (
        (1.0 if open_to_work else 0.0) * weights["open_to_work"] +
        rr_norm * weights["recruiter_response_rate"] +
        icr_norm * weights["interview_completion_rate"] +
        sa_norm * weights["search_appearances"] +
        saved_norm * weights["saved_by_recruiters"] +
        pv_norm * weights["profile_views"] +
        last_active_norm * weights["last_active"]
    )

    availability = min(1.0, max(0.0, (1.0 if open_to_work else 0.0) * 0.6 + last_active_norm * 0.3 + notice_norm * 0.1))

    behavioral_multiplier = 1.0
    if open_to_work:
        behavioral_multiplier += 0.05
    if recruiter_response_rate > 0.5:
        behavioral_multiplier += 0.05
    if interview_completion_rate > 0.7:
        behavioral_multiplier += 0.05
    if profile_views > 20:
        behavioral_multiplier += 0.05
    if last_active_days is not None and last_active_days != float("inf") and last_active_days > 60:
        behavioral_multiplier -= 0.05
    if notice_period_days is not None and notice_period_days > 60:
        behavioral_multiplier -= 0.05
    behavioral_multiplier = max(0.5, min(1.5, behavioral_multiplier))

    return {
        "open_to_work": open_to_work,
        "recruiter_response_rate": float(rr_norm),
        "interview_completion_rate": float(icr_norm),
        "search_appearances": float(search_appearances),
        "saved_by_recruiters": float(saved_by_recruiters),
        "profile_views": float(profile_views),
        "last_active_days": float(last_active_days) if last_active_days != float("inf") else None,
        "notice_period_days": float(notice_period_days) if notice_period_days is not None else None,
        "behavior_super_score": float(behavior_super_score),
        "behavioral_multiplier": float(behavioral_multiplier),
        "availability": float(availability),
    }
