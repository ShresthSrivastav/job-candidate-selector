from __future__ import annotations
import streamlit as st
import os
import time
from ui.utils.pipeline_runner import run_pipeline
from ui.components.badges import page_header, success_box, error_box

st.set_page_config(page_title="RedRobe — Ranking", layout="wide")

page_header("Run Ranking Pipeline", "Execute the Phase 4.6 ranking pipeline.")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "Data")

jd_path = os.path.join(DATA_DIR, "job_description.txt")
candidates_path = os.path.join(DATA_DIR, "candidates.jsonl")
candidates_gz = candidates_path + ".gz"

jd_ok = os.path.isfile(jd_path)
cand_ok = os.path.isfile(candidates_path) or os.path.isfile(candidates_gz)

col1, col2 = st.columns(2)
with col1:
    st.metric("JD Uploaded", "Yes" if jd_ok else "No")
with col2:
    st.metric("Candidates Uploaded", "Yes" if cand_ok else "No")

if not jd_ok or not cand_ok:
    error_box("Upload both JD and candidates files before running the pipeline.")
    st.stop()

st.divider()
st.markdown("### Pipeline Configuration")
st.caption("Candidates file: Data/candidates.jsonl")
st.caption("JD file: Data/job_description.txt")
st.caption("Output: outputs/phase46_submission.csv")

if st.button("Run Pipeline", type="primary", use_container_width=True):
    progress_bar = st.progress(0, text="Starting pipeline...")
    log_area = st.expander("Pipeline Log", expanded=True)
    log_container = log_area.empty()
    log_lines = []

    start = time.time()

    for i, line in enumerate(run_pipeline(project_dir=ROOT)):
        log_lines.append(line)
        log_container.code("\n".join(log_lines[-50:]), language="")
        if "Phase 4.5 complete" in line:
            progress_bar.progress(0.4, text="Phase 4.5 complete - running ranking...")
        elif "Phase 4.6 complete" in line:
            progress_bar.progress(0.7, text="Ranking complete - finalizing...")
        elif "Pipeline complete" in line:
            progress_bar.progress(0.9, text="Generating outputs...")
        elif "ERROR" in line:
            error_box(f"Pipeline error: {line}")
            st.stop()

    elapsed = time.time() - start
    progress_bar.progress(1.0, text="Pipeline complete!")
    st.session_state.outputs_exist = True

    st.divider()
    success_box(f"Pipeline completed in {elapsed:.2f}s")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Time", f"{elapsed:.2f}s")
    with col2:
        st.metric("Phase", "4.6")
    with col3:
        st.metric("Submission", "Ready")
