"""Disclaimer section. Owner: <student>. Words live in content/disclaimer.md."""
import streamlit as st

from lib import content
from lib.i18n import t


def render():
    c = content.load("disclaimer")
    st.title(t("nav_disclaimer"))
    st.markdown(c["intro"])
    st.markdown(c["points"])
