"""Disclaimer section. Owner: <student>. Words live in content/disclaimer.md."""
import streamlit as st

from lib import content


def render():
    c = content.load("disclaimer")
    st.title("Disclaimer")
    st.markdown(c["intro"])
    st.markdown(c["points"])
