from __future__ import annotations
import streamlit as st
import os
from ui.utils.data_loader import load_top100_json, get_output_paths, outputs_exist
from ui.components.charts import feature_contribution_chart, honeypot_gauge
from ui.components.metrics import metric_card
from ui.components.badges import page_header, info_box

st.set_page_config(page_title="RedRobe — Candidate Detail", layout="wide")

page_header("Candidate Detail View", "Full breakdown of an individual candidate's ranking.")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not outputs_exist(ROOT):
    info_box("No results found. Run the pipeline first.")
    st.stop()

paths = get_output_paths(ROOT)
top100 = load_top100_json(paths["top100_json"])

candidate_ids = [r.get("candidate_id", "?") for r in top100]
selected_id = st.selectbox("Select Candidate", candidate_ids, index=0)

row = next(r for r in top100 if r.get("candidate_id") == selected_id)

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(f"### {row.get('candidate_id', 'N/A')}")
    st.markdown(f"**Title:** {row.get('profile_title', 'N/A')}")
    st.markdown(f"**Rank:** #{row.get('rank', 'N/A')}")
    st.markdown(f"**Final Score:** {row.get('final_score', 'N/A')}")

with col2:
    hp = float(row.get("honeypot_probability", 0) or 0)
    honeypot_gauge(hp)

st.divider()
st.markdown("### Reasoning")
st.info(row.get("reasoning", "No reasoning available"))

st.divider()
st.markdown("### Feature Breakdown")

m1, m2, m3, m4 = st.columns(4)
with m1:
    metric_card("JD Coverage", f"{float(row.get('jd_coverage', 0) or 0):.4f}")
with m2:
    metric_card("Retrieval Intelligence", f"{float(row.get('retrieval_intelligence', 0) or 0):.4f}")
with m3:
    metric_card("Evidence Score", f"{float(row.get('evidence_score', 0) or 0):.4f}")
with m4:
    metric_card("Ownership Score", f"{float(row.get('ownership_score', 0) or 0):.4f}")

m5, m6, m7, m8 = st.columns(4)
with m5:
    metric_card("Career Alignment", f"{float(row.get('career_alignment_score', 0) or 0):.4f}")
with m6:
    metric_card("Behavior Score", f"{float(row.get('behavior_super_score', 0) or 0):.4f}")
with m7:
    metric_card("Availability", f"{float(row.get('availability', 0) or 0):.4f}")
with m8:
    bm = float(row.get("behavioral_multiplier", 1.0) or 1.0)
    metric_card("Behavioral Multiplier", f"{bm:.2f}x")

feature_contribution_chart(row)
