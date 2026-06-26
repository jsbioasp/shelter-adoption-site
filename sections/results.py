"""Results section. Owner: <student>.

Layout + live numbers + table logic. The words live in content/<lang>/results.md;
chrome (headers, metric labels, table columns/values) comes from lib.i18n. The
deployed AUCs and calibration are read live and filled into the {braces}.
"""
import pandas as pd
import streamlit as st

from lib import content, data, glossary, models
from lib.i18n import t


@st.cache_resource
def _live_aucs():
    return models.ensemble_aucs()


def render():
    c = content.load("results")
    st.title(t("nav_results"))

    st.markdown(c["score_meaning"])
    glossary.render(st, "auc", "calibration", "ece", "cnn", "multitask", "pp")

    st.markdown("## " + t("res_h_models"))
    aucs = _live_aucs()
    c1, c2 = st.columns(2)
    c1.metric(t("res_m_data_auc"), f"{aucs['tabular_only']:.3f}", help=t("res_help_data"))
    c2.metric(t("res_m_photo_auc"), f"{aucs['multitask']:.3f}", help=t("res_help_photo"))
    st.caption(c["auc_caption"])

    st.markdown("## " + t("res_h_ladder"))
    f = data.FINDINGS
    cfg, auc, note = t("res_col_config"), t("res_col_auc"), t("res_col_note")
    ladder = pd.DataFrame([
        {cfg: t("res_ladder_demo"), auc: f"{aucs['tabular_only']:.3f}", note: t("res_note_columns")},
        {cfg: t("res_ladder_mt"), auc: f"{aucs['multitask']:.3f}", note: t("res_note_serves")},
        {cfg: t("res_ladder_best"), auc: f"{f['m06_multitask_auc']['value']}", note: t("res_note_experiments")},
        {cfg: t("res_ladder_ceiling"), auc: f"{f['m06_ceiling_auc']['value']}", note: t("res_note_experiments")},
    ])
    st.table(ladder)
    st.caption(c["ladder_caption"])

    st.markdown("## " + t("res_h_what_we_found"))
    _findings = [
        c["photos_win"].format(lift=f["m06_multitask_lift"]["value"]),
        c["one_lever"].format(caged=f["caged_rate_gap"]["value"]),
        c["older_dog_signal"],
        c["photo_count"],
        c["tabular_ceiling"].format(ceiling=f["m05_accuracy_ceiling"]["value"]),
        c["sentiment_null"],
    ]
    st.markdown("\n".join(f"- {item}" for item in _findings))
    st.markdown("#### " + t("res_h_signal"))
    st.markdown(c["signal_mechanism"])

    _render_calibration(c)

    st.markdown("## " + t("res_h_confident"))
    st.markdown(c["confident_about"])
    st.caption(c["photo_preliminary"])


def _render_calibration(c):
    cal = data.load_calibration()
    if not cal:
        st.info("Calibration not computed yet — run `python scripts/compute_calibration.py`.")
        return
    models_cal = cal["models"]
    di = models_cal["data_image"]
    n_test = cal["n_test"]

    st.markdown("## " + t("res_h_calibration"))
    st.markdown(c["calibration_intro"].format(n_test=n_test))

    rows = []
    for b in di["bins"]:
        if b["n"] == 0:
            continue
        rows.append({
            t("res_col_pred_range"): f"{b['lo']:.0%}–{b['hi']:.0%}",
            t("res_col_dogs"): b["n"],
            t("res_col_actual"): f"{b['actual_pct']:.1f}%",
            t("res_col_gap"): f"{b['gap_pp']:+.1f}",
        })
    st.table(pd.DataFrame(rows))
    st.caption(c["calibration_caption"].format(
        ece=di["ece"], image_ece=models_cal["image_only"]["ece"]))

    st.markdown("## " + t("res_h_thresholds"))
    st.markdown(c["thresholds_intro"])
    trows = []
    for thr in di["thresholds"]:
        label = t("res_thr_all") if thr["threshold"] == 0.5 else f"≥ {thr['threshold']:.0%}" + t("res_thr_sure_suffix")
        trows.append({
            t("res_col_act"): label,
            t("res_col_covered"): f"{thr['coverage_pct']:.0f}%",
            t("res_col_accuracy"): f"{thr['accuracy_pct']:.0f}%" if thr["accuracy_pct"] is not None else "—",
        })
    st.table(pd.DataFrame(trows))
    st.caption(c["thresholds_caption"])

    st.markdown(c["why_multitask"].format(ece=di["ece"]))
