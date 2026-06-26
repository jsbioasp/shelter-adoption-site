"""Landing / Motivation section. Owner: <student>.

Layout + logic only. The words live in content/motivation.md — edit them there.
"""
import streamlit as st

from lib import content


def render():
    c = content.load("motivation")
    st.title("Shelter Adoption ML")
    st.markdown(c["tagline"])

    st.markdown("## Research background and motivation")
    st.markdown(c["research_background"])

    st.markdown("## Research objectives")
    st.markdown(c["research_objectives"])

    st.markdown("## Methodology and implementation")
    st.markdown(c["methodology"])

    st.markdown("## Expected contributions")
    st.markdown(c["expected_contributions"])

    st.markdown("## What you can do here")
    st.markdown(c["what_you_can_do"])

    st.info(c["honest_framing"])

    st.markdown("## Authors")
    st.markdown(c["authors"])
