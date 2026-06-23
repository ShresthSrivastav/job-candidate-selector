from __future__ import annotations
import streamlit as st
import os
from ui.utils.data_loader import load_top100_json, get_output_paths, outputs_exist, get_pipeline_stats
from ui.components.charts import score_distribution, experience_distribution, correlation_heatmap
from ui.components.metrics import metric_card
from ui.components.badges import page_header, info_box

st.set_page_config(page_title="RedRobe — Analytics", layout="wide")

page_header("Analytics Dashboard", "Score distributions, feature analysis, and correlation insights.")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not outputs_exist(ROOT):
    info_box("No results found. Run the pipeline first.")
    st.stop()

paths = get_output_paths(ROOT)
top100 = load_top100_json(paths["top100_json"])
stats = get_pipeline_stats(top100)

scores = [float(r.get("final_score", 0) or 0) for r in top100]

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Top-100 Candidates", str(stats["count"]))
with c2:
    metric_card("Specialists", f"{stats['specialist_pct']}%")
with c3:
    metric_card("Zero Retrieval", str(stats["zero_retrieval"]))
with c4:
    metric_card("High Honeypot Risk", str(stats["high_honeypot_risk"]))

st.divider()
c5, c6, c7, c8 = st.columns(4)
with c5:
    metric_card("Score Min", f"{stats['score_min']:.2f}")
with c6:
    metric_card("Score Max", f"{stats['score_max']:.2f}")
with c7:
    metric_card("Score Mean", f"{stats['score_mean']:.2f}")
with c8:
    metric_card("Score Spread", f"{stats['score_spread']:.2f}")

st.divider()
score_distribution(scores, title="Score Distribution (Top-100)")
experience_distribution(top100)
correlation_heatmap(top100)
