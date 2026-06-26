"""Models UI section — the core "run the model on your dog" feature. Owner: <student>.

Page prose lives in content/<lang>/models.md; the form labels, confidence tiers,
and per-result captions come from lib.i18n (they're tied to the scoring logic).
Widgets whose VALUE drives logic (Sex, Match strictness) keep English values and
only translate their display via format_func.

Three modes: Data only / Image only / Data + image. All scoring runs on CPU.
"""
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from lib import content, features, glossary, models
from lib.i18n import t

_EXEMPLARS_DIR = Path(__file__).resolve().parent.parent / "data" / "exemplars"
_EXEMPLARS_CSV = _EXEMPLARS_DIR.parent / "exemplars.csv"


def _confidence(p: float) -> tuple[str, str]:
    """Map an adoption-pace score to a tier label + plain-language read."""
    pct = f"{p:.0%}"
    if p >= 0.60:
        return t("mu_tier_faster"), t("mu_read_faster").format(p=pct)
    if p >= 0.40:
        return t("mu_tier_about"), t("mu_read_about").format(p=pct)
    return t("mu_tier_slower"), t("mu_read_slower").format(p=pct)


def _sex_radio(key=None):
    """Sex radio that displays the localized label but returns 'Female'/'Male'."""
    return st.radio(t("mu_sex"), ["Female", "Male"], horizontal=True, key=key,
                    format_func=lambda v: t("mu_female") if v == "Female" else t("mu_male"))


def _show_result(p: float, stratum: str | None = None, model: str = "data_image",
                 calibrated: bool = True):
    tier, read = _confidence(p)
    c1, c2 = st.columns([1, 2])
    c1.metric(t("mu_metric_pace"), f"{p:.0%}", help=t("mu_help_pace"))
    c2.markdown(f"### {tier}\n{read}")
    if calibrated:
        c = models.confidence_from_prob(p, model=model)
        acc = f"~{c['accuracy_pct']:.0f}%" if c["accuracy_pct"] is not None else "—"
        st.caption(t("mu_cap_calibrated").format(acc=acc))
    else:
        st.caption(t("mu_cap_uncalibrated"))
    if stratum:
        st.caption(t("mu_cap_stratum").format(stratum=stratum))
    st.caption(t("mu_cap_observational"))


def _show_features(s6):
    """Show the 6-feature SHARED_6 vector the model actually receives."""
    st.markdown("#### " + t("mu_features_header"))
    st.caption(t("mu_features_caption"))
    st.table([{t("mu_col_feature"): t(f"mu_feat_{name}"), t("mu_col_value"): int(val)}
              for name, val in zip(models.SHARED6_FEATURES, s6)])


# ---------------- Re-shoot: real same-profile dogs with strong photos ----------------
@st.cache_data
def _reshoot_pool():
    return pd.read_csv(_EXEMPLARS_CSV)


def _reshoot_pace(p: float) -> str:
    if p >= 0.60:
        return t("mu_pace_faster")
    return t("mu_pace_about") if p >= 0.40 else t("mu_pace_slower")


def _reshoot_tab(c):
    st.markdown(c["reshoot_tab"])
    st.warning(c["reshoot_experimental_note"])
    with st.form("reshoot"):
        age = st.slider(t("mu_age"), 0, 120, 8, key="rs_age")
        mixed = st.checkbox(t("mu_mixed"), value=True, key="rs_mixed")
        gender = _sex_radio(key="rs_gender")
        sterilized = st.checkbox(t("mu_fixed"), value=False, key="rs_ster")
        strict = st.select_slider(
            t("mu_match_strict"), options=["Exact profile", "Close", "Loose"], value="Close",
            format_func=lambda v: {"Exact profile": t("mu_match_exact"),
                                   "Close": t("mu_match_close"), "Loose": t("mu_match_loose")}[v],
            help=t("mu_match_help"))
        k = st.slider(t("mu_how_many"), 3, 12, 6, key="rs_k")
        up = st.file_uploader(t("mu_upload_optional"), type=["jpg", "jpeg", "png"], key="rs_up")
        go = st.form_submit_button(t("mu_find_examples"), type="primary")
    if not go:
        return

    s6 = features.derive_shared6(age, mixed, gender, sterilized)
    max_mismatch = {"Exact profile": 0, "Close": 1, "Loose": 2}[strict]

    if up is not None:
        img = Image.open(BytesIO(up.read()))
        u1, u2 = st.columns([1, 2])
        u1.image(img, width=240, caption=t("mu_your_dog"))
        with st.spinner(t("mu_spinner_score_photo")):
            p_you = models.score_data_and_image(img, s6)
        u2.metric(t("mu_your_dog_score"), f"{p_you:.0%}")
        u2.caption(c["reshoot_your_dog_caption"])

    pool = _reshoot_pool()
    target = {"is_young": int(s6[1]), "is_mixed_breed": int(s6[2]),
              "gender_male": int(s6[3]), "sterilized_yes": int(s6[5])}
    dist = sum((pool[b] != v).astype(int) for b, v in target.items())
    hits = pool.assign(mismatch=dist)
    hits = hits[hits["mismatch"] <= max_mismatch].sort_values(
        ["mismatch", "quality"], ascending=[True, False]).head(k)

    st.subheader(t("mu_reshoot_subheader").format(n=len(hits), stratum=features.stratum_label(s6)))
    if hits.empty:
        st.info(t("mu_no_matches"))
        return
    st.caption(c["reshoot_quality_note"])
    cols = st.columns(3)
    for i, (_, r) in enumerate(hits.iterrows()):
        with cols[i % 3]:
            st.image(str(_EXEMPLARS_DIR / f"{r['PetID']}.jpg"), width=240)
            badge = t("mu_badge_adopted") if r["adopted_30d"] else t("mu_badge_slower")
            match = t("mu_match_exact_label") if r["mismatch"] == 0 else t("mu_match_differ").format(n=int(r["mismatch"]))
            st.caption(f"{t('mu_word_quality')} **{r['quality']:.2f}** · {t('mu_word_pace')} "
                       f"{_reshoot_pace(r['byu'])} ({r['byu']:.0%}) · {badge} · {match}")
    st.markdown("---")
    st.markdown(c["reshoot_takeaway"])
    st.caption(c["reshoot_honesty_caption"])


def render():
    c = content.load("models")
    st.title(t("nav_models_ui"))
    st.markdown(c["intro"])
    glossary.render(st, "auc", "mlp", "cnn", "multitask", "strata")

    tab_data, tab_image, tab_both, tab_reshoot = st.tabs(
        [t("mu_tab_data"), t("mu_tab_image"), t("mu_tab_both"), t("mu_tab_reshoot")]
    )

    # ---------------- Data only ----------------
    with tab_data:
        st.markdown(c["data_tab"])
        with st.form("data_only"):
            age = st.slider(t("mu_age"), 0, 120, 8)
            mixed = st.checkbox(t("mu_mixed"), value=True)
            gender = _sex_radio()
            sterilized = st.checkbox(t("mu_fixed"), value=False)
            go = st.form_submit_button(t("mu_score"), type="primary")
        if go:
            s6 = features.derive_shared6(age, mixed, gender, sterilized)
            p = models.score_data_only(s6)
            _show_result(p, features.stratum_label(s6), model="tabular_only")
            _show_features(s6)
            st.caption(c["data_heads_up"])

    # ---------------- Image only ----------------
    with tab_image:
        st.markdown(c["image_tab"])
        up = st.file_uploader(t("mu_dog_photo"), type=["jpg", "jpeg", "png"], key="img_only")
        if up is not None:
            img = Image.open(BytesIO(up.read()))
            st.image(img, width=320, caption=t("mu_your_photo"))
            with st.spinner(t("mu_spinner_encode")):
                p = models.score_image_only(img)
            _show_result(p, model="image_only", calibrated=False)
            st.caption(c["image_axis_caption"])

    # ---------------- Data + image ----------------
    with tab_both:
        st.markdown(c["both_tab"])
        with st.form("data_image", clear_on_submit=False):
            up2 = st.file_uploader(t("mu_dog_photo"), type=["jpg", "jpeg", "png"], key="img_both")
            age2 = st.slider(t("mu_age"), 0, 120, 8, key="age2")
            mixed2 = st.checkbox(t("mu_mixed"), value=True, key="mixed2")
            gender2 = _sex_radio(key="gender2")
            ster2 = st.checkbox(t("mu_fixed"), value=False, key="ster2")
            go2 = st.form_submit_button(t("mu_score"), type="primary")
        if go2:
            if up2 is None:
                st.error(t("mu_err_upload"))
            else:
                img2 = Image.open(BytesIO(up2.read()))
                st.image(img2, width=320, caption=t("mu_your_photo"))
                s6 = features.derive_shared6(age2, mixed2, gender2, ster2)
                with st.spinner(t("mu_spinner_encode")):
                    p = models.score_data_and_image(img2, s6)
                _show_result(p, features.stratum_label(s6), model="data_image")
                _show_features(s6)

    # ---------------- Re-shoot (experimental) ----------------
    with tab_reshoot:
        _reshoot_tab(c)
