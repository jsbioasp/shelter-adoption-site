"""Landing / Motivation section. Owner: <student>.

Layout + logic only. The words live in content/motivation.md — edit them there.
"""
import streamlit as st

from lib import content


def render():
    c = content.load("motivation")
    st.title("🐕 Shelter Adoption ML")
    st.markdown(c["tagline"])

    st.markdown("## Why this matters")
    col1, col2, col3 = st.columns(3)
    col1.markdown(c["help_shelters"])
    col2.markdown(c["efficiency"])
    col3.markdown(c["social"])

    st.markdown("## What you can do here")
    st.markdown(c["what_you_can_do"])

    st.info(c["honest_framing"])
