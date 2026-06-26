"""Shelter Adoption ML — site entry point.

Each section is a self-contained module under sections/ with a render() function,
so students can co-own one site: you edit your section's file, open a PR, and the
nav wires it in here. Streamlit Community Cloud auto-redeploys on merge to main.
"""
import streamlit as st

from sections import (
    motivation, datasets, models_used, results, models_ui, discover, next_steps, disclaimer,
)

st.set_page_config(
    page_title="Shelter Adoption ML",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = [
    st.Page(motivation.render, title="Introduction and Motivations", url_path="motivation", default=True),
    st.Page(datasets.render, title="Datasets & Experiments", url_path="datasets"),
    st.Page(models_used.render, title="Models Used", url_path="models-used"),
    st.Page(results.render, title="Results", url_path="results"),
    st.Page(models_ui.render, title="Try the Models", url_path="models"),
    st.Page(discover.render, title="Discover Dogs", url_path="discover"),
    st.Page(next_steps.render, title="Next Steps", url_path="next-steps"),
    st.Page(disclaimer.render, title="Disclaimer", url_path="disclaimer"),
]

selected = st.navigation(PAGES)

# Track whether this rerun is a fresh navigation to a different page (vs an
# in-page interaction like opening a dialog). Sections can read
# st.session_state["just_navigated"] to refresh on page load without resetting
# on every widget click — Discover Dogs uses it to reshuffle per visit.
st.session_state["just_navigated"] = st.session_state.get("active_page") != selected.url_path
st.session_state["active_page"] = selected.url_path

selected.run()
