"""Models UI section — the core "run the model on your dog" feature. Owner: <student>.

Page prose lives in content/models.md (edit it there). The form controls, the
confidence tiers, and the per-result captions stay here — they're tied to the
scoring logic.

Three modes matching the wireframe:
  - Data only   -> tabular model on 6 demographics
  - Image only  -> photo model, demographics zeroed
  - Data + image-> the full multi-task model

All scoring runs on CPU in well under a second (the photo encoder warms up once).
"""
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from lib import content, features, glossary, models

_EXEMPLARS_DIR = Path(__file__).resolve().parent.parent / "data" / "exemplars"
_EXEMPLARS_CSV = _EXEMPLARS_DIR.parent / "exemplars.csv"


def _confidence(p: float) -> tuple[str, str]:
    """Map an adoption-pace score to a tier label + plain-English read.

    0.5 is the average pace: the 30-day training cutoff split PetFinder ~50/50,
    so the tiers read as faster / around / slower than a typical dog.
    """
    if p >= 0.60:
        return "🟢 Faster than average", (f"Scores {p:.0%} — above the 50% average, so this dog "
                                          "looks likely to be adopted faster than a typical dog.")
    if p >= 0.40:
        return "🟡 About average", (f"Scores {p:.0%} — near the 50% average pace. A better photo "
                                    "or a featured listing can still nudge it up.")
    return "🔴 Slower than average", (f"Scores {p:.0%} — below the 50% average, so this dog likely "
                                      "adopts slower than typical. It benefits most from a better "
                                      "photo, a featured listing, or an early foster.")


def _show_result(p: float, stratum: str | None = None, model: str = "data_image",
                 calibrated: bool = True):
    tier, read = _confidence(p)
    c1, c2 = st.columns([1, 2])
    c1.metric("Adoption pace", f"{p:.0%}",
              help="50% = average pace (our 30-day training cutoff split PetFinder ~50/50). "
                   "Higher = likely faster than a typical dog; lower = slower.")
    c2.markdown(f"### {tier}\n{read}")
    if calibrated:
        c = models.confidence_from_prob(p, model=model)
        acc = f"~{c['accuracy_pct']:.0f}%" if c["accuracy_pct"] is not None else "—"
        st.caption(f"Confidence: among dogs the model is this sure about, it's right **{acc}** "
                   "of the time. This is a *calibrated* score — predicted ≈ actual "
                   "(see Results). Pace ≠ confidence: a confident *slow* score is still "
                   "a slow score.")
    else:
        st.caption("⚠️ Photo-only is a **diagnostic**, not a calibrated probability "
                   "(it's less calibrated than the photo+data model — see Results). "
                   "Read it as 'what the picture suggests', not a reliable adoption rate.")
    if stratum:
        st.caption(f"Demographic group: **{stratum}** — effects like the photo lever are "
                   "measured within a group, so we compare like with like.")
    st.caption("Observational, not causal. Use to triage, not to decide.")


_FEATURE_LABELS = {
    "age_adult": "age_adult — age ≥ 12 months",
    "is_young": "is_young — age < 6 months",
    "is_mixed_breed": "is_mixed_breed",
    "gender_male": "gender_male",
    "gender_female": "gender_female",
    "sterilized_yes": "sterilized_yes",
}


def _show_features(s6):
    """Show the 6-feature SHARED_6 vector the model actually receives.

    The form asks four questions, but the model takes six features: the age answer
    becomes two (adult? and young?) and the sex answer becomes two (male? and
    female?). Showing the vector makes that 4 → 6 expansion explicit.
    """
    with st.expander("What the model actually sees — 6 features from your 4 answers"):
        st.caption("Your **age** answer becomes two features (`age_adult` and `is_young`) and "
                   "your **sex** answer becomes two (`gender_male`, `gender_female`). With "
                   "`is_mixed_breed` and `sterilized_yes`, that's the SHARED_6 vector.")
        st.table([{"feature": _FEATURE_LABELS[name], "value": int(val)}
                  for name, val in zip(models.SHARED6_FEATURES, s6)])


# ---------------- Re-shoot: real same-profile dogs with strong photos ----------------
# No generation (SDXL+ControlNet can't run on Streamlit Cloud's CPU). Instead, retrieve
# real PetFinder dogs with the same SHARED_6 profile and high-quality photos from a
# curated pool (data/exemplars/, built by trial/curate_exemplars.py). Pure pandas.
_RESHOOT_MATCH_BITS = ["is_young", "is_mixed_breed", "gender_male", "sterilized_yes"]


@st.cache_data
def _reshoot_pool():
    return pd.read_csv(_EXEMPLARS_CSV)


def _reshoot_pace(p: float) -> str:
    if p >= 0.60:
        return "🟢 faster"
    return "🟡 average" if p >= 0.40 else "🔴 slower"


def _reshoot_tab(c):
    st.markdown(c["reshoot_tab"])
    st.warning(c["reshoot_experimental_note"])
    with st.form("reshoot"):
        age = st.slider("Age (months)", 0, 120, 8, key="rs_age")
        mixed = st.checkbox("Mixed-breed", value=True, key="rs_mixed")
        gender = st.radio("Sex", ["Female", "Male"], horizontal=True, key="rs_gender")
        sterilized = st.checkbox("Spayed / neutered", value=False, key="rs_ster")
        strict = st.select_slider(
            "Match strictness", options=["Exact profile", "Close", "Loose"], value="Close",
            help="How closely the example dogs must match. Exact = all 4 demographic traits "
                 "identical; Loose = up to 2 can differ (more examples, less similar).")
        k = st.slider("How many examples", 3, 12, 6, key="rs_k")
        up = st.file_uploader("Optional: your dog's photo (to see its score for contrast)",
                              type=["jpg", "jpeg", "png"], key="rs_up")
        go = st.form_submit_button("Find good-photo examples", type="primary")
    if not go:
        return

    s6 = features.derive_shared6(age, mixed, gender, sterilized)
    max_mismatch = {"Exact profile": 0, "Close": 1, "Loose": 2}[strict]

    if up is not None:
        img = Image.open(BytesIO(up.read()))
        u1, u2 = st.columns([1, 2])
        u1.image(img, width=240, caption="Your dog")
        with st.spinner("Scoring your photo…"):
            p_you = models.score_data_and_image(img, s6)
        u2.metric("Your dog's adoption-pace score", f"{p_you:.0%}")
        u2.caption(c["reshoot_your_dog_caption"])

    pool = _reshoot_pool()
    target = {"is_young": int(s6[1]), "is_mixed_breed": int(s6[2]),
              "gender_male": int(s6[3]), "sterilized_yes": int(s6[5])}
    dist = sum((pool[b] != v).astype(int) for b, v in target.items())
    hits = pool.assign(mismatch=dist)
    hits = hits[hits["mismatch"] <= max_mismatch].sort_values(
        ["mismatch", "quality"], ascending=[True, False]).head(k)

    st.subheader(f"{len(hits)} real dogs — {features.stratum_label(s6)}, strong listing photos")
    if hits.empty:
        st.info("No close matches in the curated pool — try a looser match strictness.")
        return
    cols = st.columns(3)
    for i, (_, r) in enumerate(hits.iterrows()):
        with cols[i % 3]:
            st.image(str(_EXEMPLARS_DIR / f"{r['PetID']}.jpg"), width=240)
            badge = "✅ adopted ≤30d" if r["adopted_30d"] else "○ slower adopt"
            match = "exact profile" if r["mismatch"] == 0 else f"{int(r['mismatch'])} trait(s) differ"
            st.caption(f"photo-quality **{r['quality']:.2f}** · pace {_reshoot_pace(r['byu'])} "
                       f"({r['byu']:.0%}) · {badge} · {match}")
    st.markdown("---")
    st.markdown(c["reshoot_takeaway"])
    st.caption(c["reshoot_honesty_caption"])


def render():
    c = content.load("models")
    st.title("Try the Models")
    st.markdown(c["intro"])
    glossary.render(st, "mlp", "cnn", "multitask", "strata")

    tab_data, tab_image, tab_both, tab_reshoot = st.tabs(
        ["📋 Data only", "📷 Image only", "📋📷 Data + image", "📸 Re-shoot (experimental)"]
    )

    # ---------------- Data only ----------------
    with tab_data:
        st.markdown(c["data_tab"])
        with st.form("data_only"):
            age = st.slider("Age (months)", 0, 120, 8)
            mixed = st.checkbox("Mixed-breed", value=True)
            gender = st.radio("Sex", ["Female", "Male"], horizontal=True)
            sterilized = st.checkbox("Spayed / neutered", value=False)
            go = st.form_submit_button("Score", type="primary")
        if go:
            s6 = features.derive_shared6(age, mixed, gender, sterilized)
            p = models.score_data_only(s6)
            _show_result(p, features.stratum_label(s6), model="tabular_only")
            _show_features(s6)
            st.caption(c["data_heads_up"])

    # ---------------- Image only ----------------
    with tab_image:
        st.markdown(c["image_tab"])
        up = st.file_uploader("Dog photo", type=["jpg", "jpeg", "png"], key="img_only")
        if up is not None:
            img = Image.open(BytesIO(up.read()))
            st.image(img, width=320, caption="Your photo")
            with st.spinner("Encoding photo + scoring…"):
                p = models.score_image_only(img)
            _show_result(p, model="image_only", calibrated=False)
            st.caption(c["image_axis_caption"])

    # ---------------- Data + image ----------------
    with tab_both:
        st.markdown(c["both_tab"])
        with st.form("data_image", clear_on_submit=False):
            up2 = st.file_uploader("Dog photo", type=["jpg", "jpeg", "png"], key="img_both")
            age2 = st.slider("Age (months)", 0, 120, 8, key="age2")
            mixed2 = st.checkbox("Mixed-breed", value=True, key="mixed2")
            gender2 = st.radio("Sex", ["Female", "Male"], horizontal=True, key="gender2")
            ster2 = st.checkbox("Spayed / neutered", value=False, key="ster2")
            go2 = st.form_submit_button("Score", type="primary")
        if go2:
            if up2 is None:
                st.error("Upload a photo to use the combined model (or use the Data-only tab).")
            else:
                img2 = Image.open(BytesIO(up2.read()))
                st.image(img2, width=320, caption="Your photo")
                s6 = features.derive_shared6(age2, mixed2, gender2, ster2)
                with st.spinner("Encoding photo + scoring…"):
                    p = models.score_data_and_image(img2, s6)
                _show_result(p, features.stratum_label(s6), model="data_image")
                _show_features(s6)

    # ---------------- Re-shoot (experimental) ----------------
    with tab_reshoot:
        _reshoot_tab(c)
