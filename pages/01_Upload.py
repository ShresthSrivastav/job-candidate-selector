from __future__ import annotations
import streamlit as st
import os
from ui.utils.validators import validate_txt_file, validate_jsonl_file
from ui.components.badges import page_header, success_box, error_box, info_box

st.set_page_config(page_title="RedRobe — Upload", layout="wide")

page_header("Upload Files", "Upload Job Description and Candidate data for ranking.")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "Data")
os.makedirs(DATA_DIR, exist_ok=True)

jd_path = os.path.join(DATA_DIR, "job_description.txt")
candidates_path = os.path.join(DATA_DIR, "candidates.jsonl")

if "jd_uploaded" not in st.session_state:
    st.session_state.jd_uploaded = os.path.isfile(jd_path) and validate_txt_file(jd_path)[0]
if "candidates_uploaded" not in st.session_state:
    st.session_state.candidates_uploaded = os.path.isfile(candidates_path) and validate_jsonl_file(candidates_path)[0]

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Job Description")
    jd_file = st.file_uploader("Upload .txt file", type=["txt"], key="jd_uploader")
    if jd_file:
        with open(jd_path, "wb") as f:
            f.write(jd_file.getbuffer())
        valid, msg = validate_txt_file(jd_path)
        if valid:
            st.session_state.jd_uploaded = True
            success_box(f"JD uploaded: {jd_file.name} ({len(jd_file.getvalue())} bytes)")
        else:
            st.session_state.jd_uploaded = False
            error_box(f"Validation failed: {msg}")
    if st.session_state.jd_uploaded:
        st.success("JD file ready")

with col2:
    st.markdown("### Candidates")
    cand_file = st.file_uploader("Upload .jsonl or .jsonl.gz", type=["jsonl", "gz"], key="cand_uploader")
    if cand_file:
        path = candidates_path
        if cand_file.name.endswith(".gz"):
            path = candidates_path + ".gz"
        with open(path, "wb") as f:
            f.write(cand_file.getbuffer())
        valid, msg = validate_jsonl_file(path)
        if valid:
            st.session_state.candidates_uploaded = True
            success_box(f"Candidates uploaded: {cand_file.name} ({len(cand_file.getvalue()) / 1e6:.1f} MB)")
        else:
            st.session_state.candidates_uploaded = False
            error_box(f"Validation failed: {msg}")
    if st.session_state.candidates_uploaded:
        st.success("Candidates file ready")

st.divider()
info_box("Files are saved to the Data/ directory and persist across page navigation.")
