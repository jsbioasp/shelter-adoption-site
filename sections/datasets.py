"""Datasets & Experiments section. Owner: <student>.

Layout + numbers + logic only. The words live in content/datasets.md — edit them
there. Numbers stay sourced in lib.data.FINDINGS and are filled into the {braces}.
"""
import pandas as pd
import streamlit as st

from lib import content, data, glossary


@st.cache_data
def _taiwan_summary():
    df = data.load_taiwan_dogs()
    if len(df) == 0:
        return None
    by_shelter = (df.groupby("shelter_name").size()
                  .sort_values(ascending=False).head(12))
    mixed_share = float(df["is_mixed_breed"].mean())
    return df, by_shelter, mixed_share


def render():
    c = content.load("datasets")
    f = data.FINDINGS
    r = data.TAIWAN_SHELTER_RANKING

    st.title("Datasets & Experiments")

    st.markdown("## Three datasets, three jobs")
    col1, col2, col3 = st.columns(3)
    col1.markdown(c["petfinder"])
    col2.markdown(c["austin"])
    col3.markdown(c["taiwan"])

    st.markdown("### Why dogs, why shelters")
    st.markdown(c["why_dogs"])

    st.markdown("## The catch: every dataset is broken in its own way")
    st.markdown(c["challenges_intro"])
    cc1, cc2, cc3 = st.columns(3)
    cc1.markdown(c["challenge_petfinder"])
    cc2.markdown(c["challenge_taiwan"])
    cc3.markdown(c["challenge_austin"])
    st.info(c["bias_note"])

    st.markdown("## Notable successes")
    st.success(c["rankings_success"].format(n_shelters=r["n_shelters"], spearman=r["spearman"]))
    st.table(pd.DataFrame(r["rows"]).set_index("Our rank"))
    st.caption(c["ranking_caption"].format(source=r["source"]))
    st.caption(c["ranking_scope"])
    with st.expander("How we measure transfer — and which model earns the 0.927"):
        st.markdown(c["ranking_how"])
    st.success(c["photos_win"].format(lift=f["m06_multitask_lift"]["value"]))
    st.success(c["one_lever"].format(caged=f["caged_rate_gap"]["value"]))
    st.success(c["photo_count"])

    glossary.render(st, "auc", "rank_agreement")

    st.markdown("## Notable failures (the honest part)")
    st.warning(c["photo_transfer"])
    st.info(c["photo_transfer_deep"])
    st.warning(c["tabular_ceiling"].format(ceiling=f["m05_accuracy_ceiling"]["value"]))

    summary = _taiwan_summary()
    if summary is not None:
        df, by_shelter, mixed_share = summary
        st.markdown("## The live Taiwan data, right now")
        c1, c2, c3 = st.columns(3)
        c1.metric("Adoptable dogs", f"{len(df):,}")
        c2.metric("Shelters", f"{df['shelter_name'].nunique()}")
        c3.metric("Mixed-breed share", f"{mixed_share:.0%}")
        st.markdown("**Adoptable dogs by shelter (top 12)**")
        st.bar_chart(by_shelter)
    else:
        st.info(c["taiwan_not_loaded"])
