from __future__ import annotations
import os
import streamlit as st
from ui.utils.data_loader import load_top100_json, get_output_paths, outputs_exist
from ui.components.tables import render_top100_table
from ui.components.badges import page_header, info_box

st.set_page_config(page_title="RedRobe — Results", layout="wide")

page_header("Top-100 Ranking Results", "Interactive table with search, sort, and filter.")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not outputs_exist(ROOT):
    info_box("No results found. Run the pipeline in the Ranking tab first.")
    st.stop()

paths = get_output_paths(ROOT)
top100 = load_top100_json(paths["top100_json"])

st.markdown(f"**{len(top100)}** candidates ranked | Phase 4.6")

col1, col2, col3 = st.columns(3)
with col1:
    search_id = st.text_input("Search by Candidate ID", placeholder="e.g. CAND_000")
with col2:
    score_min = st.number_input("Min Score", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
with col3:
    score_max = st.number_input("Max Score", min_value=0.0, max_value=100.0, value=100.0, step=1.0)

filtered = top100
if search_id:
    filtered = [r for r in filtered if search_id.upper() in (r.get("candidate_id") or "").upper()]
filtered = [r for r in filtered if score_min <= float(r.get("final_score", 0) or 0) <= score_max]

st.markdown(f"Showing {len(filtered)} of {len(top100)} candidates")

page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=1)
total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
start = (page - 1) * page_size
page_rows = filtered[start:start + page_size]

render_top100_table(page_rows)
st.caption(f"Page {page} of {total_pages}")
