from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime
import re


def _parse_date(d: str):
    if not d:
        return None
    try:
        return datetime.fromisoformat(d)
    except Exception:
        # try common formats
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(d, fmt)
            except Exception:
                continue
    return None


def detect_honeypot(normalized_candidate: Dict[str, Any]) -> Dict[str, Any]:
    raw = normalized_candidate.get("raw_json", {}) or {}
    ch = raw.get("career_history") or []
    flags: List[str] = []

    # duration mismatch
    for item in ch:
        sd = item.get("start_date")
        ed = item.get("end_date")
        dm = item.get("duration_months")
        sdt = _parse_date(sd)
        edt = _parse_date(ed) if ed else None
        if sdt and edt and dm is not None:
            # compute months
            delta_months = (edt.year - sdt.year) * 12 + (edt.month - sdt.month)
            if abs(delta_months - int(dm or 0)) > 3:
                flags.append("duration_mismatch")

    # overlapping jobs
    ranges = []
    for item in ch:
        sdt = _parse_date(item.get("start_date"))
        edt = _parse_date(item.get("end_date")) if item.get("end_date") else None
        if sdt:
            ranges.append((sdt, edt or datetime.max))
    ranges.sort()
    for i in range(len(ranges) - 1):
        a0, a1 = ranges[i]
        b0, b1 = ranges[i + 1]
        if a1 >= b0:
            flags.append("overlap")
            break

    # impossible dates: future start_date > today + 6 months
    now = datetime.now()
    for item in ch:
        sdt = _parse_date(item.get("start_date"))
        if sdt and sdt > now.replace(year=now.year + 1):
            flags.append("impossible_dates")
            break

    # skill inflation: many skills with zero duration
    skills = raw.get("skills") or []
    zero_dur = 0
    for s in skills:
        if (s or {}).get("duration_months") in (0, None):
            zero_dur += 1
    if skills and zero_dur / max(1, len(skills)) > 0.6:
        flags.append("skill_inflation")

    # skill density (too many skills)
    if len(skills) > 80:
        flags.append("skill_density")

    # buzzword density in career descriptions
    buzzwords = ["synergy", "leverage", "thought leader", "ninja", "rockstar", "passionate", "guru"]
    buzz_count = 0
    total_text = ""
    for item in ch:
        desc = item.get("description") or ""
        total_text += " " + desc.lower()
    for b in buzzwords:
        buzz_count += total_text.count(b)
    if len(total_text.split()) > 0 and buzz_count / max(1, len(total_text.split())) > 0.02:
        flags.append("buzzword_dense")

    # contradiction detection: title mentions "engineer" but skills all non-tech
    titles = " ".join([ (i.get("title") or "").lower() for i in ch ])
    skill_names = [ (s or {}).get("name","" ).lower() for s in skills ]
    if ("engineer" in titles or "developer" in titles) and all(not any(c.isalpha() for c in n) or n in ("",) or len(n) < 2 for n in skill_names):
        flags.append("contradiction")

    # consulting-only detection: many short gigs (<6 months)
    short_count = 0
    for item in ch:
        dm = item.get("duration_months") or 0
        try:
            if int(dm) < 6:
                short_count += 1
        except Exception:
            continue
    if ch and short_count / max(1, len(ch)) > 0.5:
        flags.append("consulting_only")

    # generic resume detection: very short descriptions
    short_descs = 0
    for item in ch:
        desc = item.get("description") or ""
        if len((desc or "").split()) < 10:
            short_descs += 1
    if ch and short_descs / max(1, len(ch)) > 0.7:
        flags.append("generic_resume")

    # compute a simple honeypot probability (more flags => higher prob)
    unique_flags = sorted(set(flags))
    prob = min(0.99, len(unique_flags) * 0.15)

    return {
        "honeypot_flags": unique_flags,
        "honeypot_probability": float(prob),
    }
