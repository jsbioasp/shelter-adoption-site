"""Models Used section — what the three model types are and what they do.

Owner: <student>. Layout only; the words live in content/models_used.md.
"""
import streamlit as st

from lib import content


def render():
    c = content.load("models_used")
    st.title("Models Used")
    st.markdown(c["intro"])
    st.markdown(c["mlp"])
    st.markdown(c["cnn"])
    st.markdown(c["multitask"])
