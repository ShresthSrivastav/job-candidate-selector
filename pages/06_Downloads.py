from __future__ import annotations
import streamlit as st
import os
from ui.utils.data_loader import get_output_paths, outputs_exist
from ui.components.badges import page_header, success_box, info_box

st.set_page_config(page_title="RedRobe — Downloads", layout="wide")

page_header("Downloads", "Export results and reports.")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not outputs_exist(ROOT):
    info_box("No results found. Run the pipeline in the Ranking tab first.")
    st.stop()

paths = get_output_paths(ROOT)

st.markdown("### Primary Outputs")

c1, c2 = st.columns(2)
with c1:
    if os.path.isfile(paths["submission"]):
        with open(paths["submission"], "rb") as f:
            st.download_button(
                label="Download phase46_submission.csv",
                data=f,
                file_name="phase46_submission.csv",
                mime="text/csv",
                use_container_width=True,
            )
        size = os.path.getsize(paths["submission"])
        st.caption(f"{size / 1024:.1f} KB")

with c2:
    if os.path.isfile(paths["top100_json"]):
        with open(paths["top100_json"], "rb") as f:
            st.download_button(
                label="Download phase46_top100.json",
                data=f,
                file_name="phase46_top100.json",
                mime="application/json",
                use_container_width=True,
            )
        size = os.path.getsize(paths["top100_json"])
        st.caption(f"{size / 1024:.1f} KB")

st.divider()
st.markdown("### Reports")

if os.path.isfile(paths["report"]):
    with open(paths["report"], "rb") as f:
        st.download_button(
            label="Download phase46_report.md",
            data=f,
            file_name="phase46_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

success_box("All files are ready.")
