"""Next Steps section. Owner: <student>. Words live in content/next_steps.md."""
import streamlit as st

from lib import content
from lib.i18n import t


def render():
    c = content.load("next_steps")
    st.title(t("nav_next_steps"))
    st.markdown(c["intro"])
    st.markdown(c["open_source"])
    st.markdown(c["website_outreach"])
    st.markdown(c["closing"])
