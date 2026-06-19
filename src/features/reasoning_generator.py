from __future__ import annotations
from typing import Dict, Any, List


def generate_reasoning(candidate: Dict[str, Any], rank: int, final_score: float) -> str:
    parts = []

    jd_cov = candidate.get("jd_coverage", 0.0) or 0.0
    ev = candidate.get("evidence_score", 0.0) or 0.0
    retr = candidate.get("retrieval_intelligence", 0.0) or 0.0
    bss = candidate.get("behavior_super_score", 0.0) or 0.0
    qual = candidate.get("candidate_quality_score", 0.0) or 0.0
    cq = candidate.get("career_quality_score", 0.0) or 0.0
    avail = candidate.get("availability", 0.0) or 0.0
    bm = candidate.get("behavioral_multiplier", 1.0) or 1.0
    hp = candidate.get("honeypot_probability", 0.0) or 0.0

    parts.append(f"Rank #{rank}")
    parts.append(f"Score={final_score:.2f}/100")

    jd_pct = round(jd_cov * 100)
    parts.append(f"JD match: {jd_pct}%")

    if ev >= 0.7:
        parts.append("Strong evidence of production ML work")
    elif ev >= 0.4:
        parts.append("Moderate evidence of ML relevance")
    elif ev > 0.0:
        parts.append("Limited ML evidence")

    retr_pct = round(retr * 100)
    skills = candidate.get("top_retrieval_skills", [])
    if isinstance(skills, str):
        skills = skills.split("|") if skills else []
    skills_str = ", ".join(skills[:3]) if skills else "none"
    parts.append(f"Retrieval expertise: {retr_pct}% ({skills_str})")

    bss_pct = round(bss * 100)
    if bss > 0.5:
        parts.append(f"High engagement (behavior score: {bss_pct}%)")
    elif bss > 0.2:
        parts.append(f"Moderate engagement (behavior score: {bss_pct}%)")
    else:
        parts.append(f"Low engagement (behavior score: {bss_pct}%)")

    qual_pct = round(qual * 100)
    cq_pct = round(cq * 100)
    parts.append(f"Quality: profile={qual_pct}%, career={cq_pct}%")

    avail_pct = round(avail * 100)
    otw = candidate.get("open_to_work", False)
    parts.append(f"Availability: {avail_pct}% (open_to_work={otw})")

    if bm != 1.0:
        parts.append(f"Behavioral multiplier: {bm:.2f}x")
    if hp > 0.3:
        parts.append(f"Honeypot risk: {round(hp * 100)}%")

    top_snippets = candidate.get("top_evidence_snippets", [])
    if isinstance(top_snippets, str):
        import json
        try:
            top_snippets = json.loads(top_snippets)
        except Exception:
            top_snippets = [top_snippets]
    if isinstance(top_snippets, list) and len(top_snippets) > 0:
        snippet_text = ""
        if isinstance(top_snippets[0], dict):
            snippet_text = top_snippets[0].get("snippet", str(top_snippets[0]))
        else:
            snippet_text = str(top_snippets[0])
        if snippet_text:
            truncated = snippet_text[:120] + "..." if len(snippet_text) > 120 else snippet_text
            parts.append(f"Evidence: \"{truncated}\"")

    return " | ".join(parts)
