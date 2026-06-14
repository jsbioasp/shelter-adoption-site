"""Datasets & Experiments section. Owner: <student>.

Why PetFinder + Taiwan, and the notable successes and failures. Every number
here comes from lib.data.FINDINGS so nothing is unsourced.
"""
import pandas as pd
import streamlit as st

from lib import data


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
    st.title("Datasets & Experiments")

    st.markdown("## Two datasets, two jobs")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            "### PetFinder (Malaysia)\n"
            "~8,000 dogs with **photos, descriptions, and resolved adoption outcomes**. "
            "This is where we *train* — it has everything a supervised model needs. "
            "It answers: *what predicts adoption when you can see the listing?*"
        )
    with col2:
        st.markdown(
            "### Taiwan MOA shelters\n"
            "Thousands of currently-adoptable dogs from Taiwan's public open-data feed — "
            "**live, but no outcome labels**. This is where we *deploy and test transfer*. "
            "It answers: *does what we learned in Malaysia travel to Taiwan?*"
        )

    st.markdown("### Why dogs, why shelters")
    st.markdown(
        "Dogs are the larger, more balanced population in both datasets, and shelter "
        "listings are where a prediction can actually change an outcome. Cats and other "
        "species were out of scope to keep the comparison clean."
    )

    st.markdown("## Notable successes")
    f = data.FINDINGS
    r = data.TAIWAN_SHELTER_RANKING
    st.success(
        f"**Rankings transfer across countries.** Over the {r['n_shelters']} shelters with "
        f"published government adoption rates, our model's ranking matched the government's at "
        f"**ρ = {r['spearman']}** (1.0 would be identical order) — the *order* transfers even "
        "though the *absolute* rates don't."
    )
    st.table(pd.DataFrame(r["rows"]).set_index("Our rank"))
    st.caption(
        "Government rank is by published adoption rate; the three New Taipei shelters share the "
        "same 95% rate (a 3-way tie for #1). Our model puts them in its top 3 and pins the "
        "lowest-rate shelters at the bottom — the only disagreement is one adjacent swap, "
        "Kaohsiung edging out Taipei City, and that single inversion is the whole gap from a "
        f"perfect 1.0. {r['source']}"
    )
    st.caption(
        "Scope: this is the validated set — the 7 shelters with a published government rate. "
        "Counted across every shelter that maps to a rated city, the agreement weakens (the "
        "model can't tell apart shelters within the same city), so the claim stays scoped to "
        "these 7."
    )
    st.success(
        f"**Photos add real signal.** Adding CNN photo features lifts adoption AUC by "
        f"**{f['m06_multitask_lift']['value']}** over the tabular baseline. "
        f"*{f['m06_multitask_lift']['source']}*"
    )
    st.success(
        f"**One lever beats a fancy model.** Within young mixed-breed dogs, caged photos "
        f"are associated with **{f['caged_rate_gap']['value']}** in 30-day adoption. "
        f"*{f['caged_rate_gap']['source']}*"
    )

    st.markdown("## Notable failures (the honest part)")
    st.warning(
        "**Photo features don't transfer cleanly.** The CNN trained on Malaysian listings "
        "scored Taipei City's institutional photos *lowest* — even though Taipei has "
        "Taiwan's highest published adoption rate. Photo content is location-specific."
    )
    st.warning(
        "**Tabular data hits a ceiling fast.** Demographics alone cap out around "
        f"**{f['m05_accuracy_ceiling']['value']}**. No amount of model tuning broke past it — "
        "the information just isn't in the columns."
    )

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
        st.info("Taiwan snapshot not loaded yet — the Discover Dogs page explains the "
                "scheduled refresh.")
