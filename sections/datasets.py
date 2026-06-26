"""Datasets & Experiments section. Owner: <student>.

Layout + numbers + logic only. The words live in content/<lang>/datasets.md;
chrome (headers, labels, table columns) comes from lib.i18n. Numbers stay sourced
in lib.data and are filled into the {braces}.
"""
import pandas as pd
import streamlit as st

from lib import content, data, glossary
from lib.i18n import t


@st.cache_data
def _taiwan_summary():
    df = data.load_taiwan_dogs()
    if len(df) == 0:
        return None
    by_shelter = (df.groupby("shelter_name").size()
                  .sort_values(ascending=False).head(12))
    mixed_share = float(df["is_mixed_breed"].mean())
    return df, by_shelter, mixed_share


def _ranking_table(rows):
    """Localize the ranking-table column headers; the values stay as sourced."""
    col_map = {
        "Our rank": t("col_our_rank"), "Shelter": t("col_shelter"),
        "Published": t("col_published"), "Our score": t("col_our_score"),
        "Gov rank": t("col_gov_rank"), "Shift": t("col_shift"),
    }
    return pd.DataFrame(rows).rename(columns=col_map).set_index(t("col_our_rank"))


def render():
    c = content.load("datasets")
    r = data.TAIWAN_SHELTER_RANKING

    st.title(t("nav_datasets"))

    st.markdown("## " + t("ds_h_three_datasets"))
    col1, col2, col3 = st.columns(3)
    col1.markdown(c["petfinder"])
    col2.markdown(c["austin"])
    col3.markdown(c["taiwan"])

    glossary.render(st, "auc", "rank_agreement", "cnn")

    st.markdown("## " + t("ds_h_purposes"))
    st.markdown(c["challenges_intro"])
    cc1, cc2, cc3 = st.columns(3)
    cc1.markdown(c["challenge_petfinder"])
    cc2.markdown(c["challenge_taiwan"])
    cc3.markdown(c["challenge_austin"])
    st.markdown(c["bias_note"])

    st.markdown("## " + t("ds_h_rankings"))
    st.markdown(c["rankings_success"].format(n_shelters=r["n_shelters"], spearman=r["spearman"]))
    st.table(_ranking_table(r["rows"]))
    st.caption(c["ranking_caption"].format(source=t("ds_ranking_source")))
    st.caption(c["ranking_scope"])
    st.markdown("#### " + t("ds_h_how_measure"))
    st.markdown(c["ranking_how"])

    summary = _taiwan_summary()
    if summary is not None:
        df, by_shelter, mixed_share = summary
        st.markdown("## " + t("ds_h_live_data"))
        c1, c2, c3 = st.columns(3)
        c1.metric(t("ds_m_adoptable"), f"{len(df):,}")
        c2.metric(t("ds_m_shelters"), f"{df['shelter_name'].nunique()}")
        c3.metric(t("ds_m_mixed_share"), f"{mixed_share:.0%}")
        st.markdown("**" + t("ds_by_shelter") + "**")
        st.bar_chart(by_shelter)
    else:
        st.markdown(c["taiwan_not_loaded"])
