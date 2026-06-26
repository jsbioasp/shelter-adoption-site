"""Landing / Introduction section. Owner: <student>.

Layout + logic only. The words live in content/<lang>/motivation.md; the section
headers come from lib.i18n so they translate with the rest of the chrome.
"""
import streamlit as st

from lib import content
from lib.i18n import t


def render():
    c = content.load("motivation")
    st.title(t("site_title"))
    st.markdown(c["tagline"])

    st.markdown("## " + t("h_research_background"))
    st.markdown(c["research_background"])

    st.markdown("## " + t("h_research_objectives"))
    st.markdown(c["research_objectives"])

    st.markdown("## " + t("h_methodology"))
    st.markdown(c["methodology"])

    st.markdown("## " + t("h_expected_contributions"))
    st.markdown(c["expected_contributions"])

    st.markdown("## " + t("h_what_you_can_do"))
    st.markdown(c["what_you_can_do"])

    st.markdown("## " + t("h_authors"))
    st.markdown(c["authors"])
