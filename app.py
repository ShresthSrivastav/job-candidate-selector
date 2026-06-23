"""RedRobe Candidate Ranking System — Streamlit Dashboard."""
from __future__ import annotations
import streamlit as st
from ui.utils.data_loader import outputs_exist, get_version

st.set_page_config(
    page_title="RedRobe Candidate Ranking",
    page_icon=":material/search:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("RedRobe")
st.sidebar.caption("Candidate Ranking System v1.1.0")

st.sidebar.page_link("app.py", label="Home", use_container_width=True)
st.sidebar.page_link("pages/01_Upload.py", label="Upload", use_container_width=True)
st.sidebar.page_link("pages/02_Ranking.py", label="Ranking", use_container_width=True)
st.sidebar.page_link("pages/03_Results.py", label="Results", use_container_width=True)
st.sidebar.page_link("pages/04_Candidate_Detail.py", label="Candidate Detail", use_container_width=True)
st.sidebar.page_link("pages/05_Analytics.py", label="Analytics", use_container_width=True)
st.sidebar.page_link("pages/06_Downloads.py", label="Downloads", use_container_width=True)

st.sidebar.divider()
st.sidebar.markdown("### Pipeline Status")
if outputs_exist():
    st.sidebar.code("Phase 4.6 submission ready")
else:
    st.sidebar.code("No submission yet")

st.sidebar.divider()
st.sidebar.caption(f"Version: {get_version()}")

st.title("RedRobe Candidate Ranking System")
st.markdown("---")

c1, c2, c3 = st.columns(3)
with c1:
    st.page_link("pages/01_Upload.py", label="1. Upload Data", use_container_width=True)
with c2:
    st.page_link("pages/02_Ranking.py", label="2. Run Ranking", use_container_width=True)
with c3:
    st.page_link("pages/03_Results.py", label="3. View Results", use_container_width=True)

st.info("Select a page from the sidebar to get started. Follow the numbered steps above.")
