"""Models UI section — the core "run the model on your dog" feature. Owner: <student>.

Three modes matching the wireframe:
  - Data only   -> tabular model on 6 demographics
  - Image only  -> photo model, demographics zeroed
  - Data + image-> the full multi-task model

All scoring runs on CPU in well under a second (the photo encoder warms up once).
"""
from io import BytesIO

import streamlit as st
from PIL import Image

from lib import features, models


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
        st.caption(f"Demographic stratum: **{stratum}** "
                   "(y = young, m = mixed-breed; the rate-gap analysis is run within strata).")
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


def render():
    st.title("Try the Models")
    st.markdown(
        "Run the adoption model on your own dog. Pick a mode — the more you give it, the "
        "more the prediction has to work with."
    )

    tab_data, tab_image, tab_both = st.tabs(
        ["📋 Data only", "📷 Image only", "📋📷 Data + image"]
    )

    # ---------------- Data only ----------------
    with tab_data:
        st.markdown("Four facts any shelter already knows — the model turns them into six "
                    "features. No photo needed.")
        with st.form("data_only"):
            age = st.slider("Age (months)", 0, 120, 8)
            mixed = st.checkbox("Mixed-breed", value=True)
            gender = st.radio("Sex", ["Female", "Male"], horizontal=True)
            sterilized = st.checkbox("Spayed / neutered", value=False)
            go = st.form_submit_button("Score", type="primary")
        if go:
            s6 = features.derive_shared6(age, mixed, gender, sterilized)
            p = models.score_data_only(s6)
            _show_result(p, features.stratum_key(s6), model="tabular_only")
            _show_features(s6)
            st.caption("Heads-up: with only 6 demographic flags, this model produces just "
                       "~16 distinct scores. For a per-dog read, add a photo.")

    # ---------------- Image only ----------------
    with tab_image:
        st.markdown("Upload a listing photo. The model reads the dog from the picture "
                    "alone (demographics zeroed) — useful for *what does the photo say?*")
        up = st.file_uploader("Dog photo", type=["jpg", "jpeg", "png"], key="img_only")
        if up is not None:
            img = Image.open(BytesIO(up.read()))
            st.image(img, width=320, caption="Your photo")
            with st.spinner("Encoding photo + scoring…"):
                p = models.score_image_only(img)
            _show_result(p, model="image_only", calibrated=False)
            st.caption("Photo-axis only: the model is reading age/breed/body cues from the "
                       "pixels, not aesthetics on their own (see the Results page).")

    # ---------------- Data + image ----------------
    with tab_both:
        st.markdown("The full model: photo **and** demographics together. This is the "
                    "configuration the Results page reports at AUC ≈ 0.70.")
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
                _show_result(p, features.stratum_key(s6), model="data_image")
                _show_features(s6)
