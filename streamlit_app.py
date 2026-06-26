"""Shelter Adoption ML — site entry point.

Each section is a self-contained module under sections/ with a render() function,
so students can co-own one site: you edit your section's file, open a PR, and the
nav wires it in here. Streamlit Community Cloud auto-redeploys on merge to main.

Bilingual: the sidebar language picker sets st.session_state["lang"] ('en'/'zh'),
which lib.content (page prose) and lib.i18n (UI chrome) both read.
"""
import streamlit as st

from lib.i18n import t
from sections import (
    motivation, datasets, models_used, results, models_ui, discover, next_steps, disclaimer,
)

st.set_page_config(
    page_title="Shelter Adoption ML",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Language picker — sets st.session_state["lang"], read by content.load + i18n.t.
# Rendered before the nav so the page titles below come out in the chosen language.
_choice = st.sidebar.radio(
    "Language / 語言", ["English", "中文"], horizontal=True,
    index=0 if st.session_state.get("lang", "en") == "en" else 1, key="lang_choice",
)
st.session_state["lang"] = "zh" if _choice == "中文" else "en"

PAGES = [
    st.Page(motivation.render, title=t("nav_motivation"), url_path="motivation", default=True),
    st.Page(datasets.render, title=t("nav_datasets"), url_path="datasets"),
    st.Page(models_used.render, title=t("nav_models_used"), url_path="models-used"),
    st.Page(results.render, title=t("nav_results"), url_path="results"),
    st.Page(models_ui.render, title=t("nav_models_ui"), url_path="models"),
    st.Page(discover.render, title=t("nav_discover"), url_path="discover"),
    st.Page(next_steps.render, title=t("nav_next_steps"), url_path="next-steps"),
    st.Page(disclaimer.render, title=t("nav_disclaimer"), url_path="disclaimer"),
]

selected = st.navigation(PAGES)

# Track whether this rerun is a fresh navigation to a different page (vs an in-page
# interaction). Discover Dogs reads st.session_state["just_navigated"] to reshuffle.
st.session_state["just_navigated"] = st.session_state.get("active_page") != selected.url_path
st.session_state["active_page"] = selected.url_path

selected.run()
