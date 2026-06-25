"""Results section. Owner: <student>.

Layout + live numbers + table logic. The words live in content/results.md — edit
them there. The deployed-model AUCs and calibration are read live from the
ensembles / calibration.json and filled into the {braces}.
"""
import pandas as pd
import streamlit as st

from lib import content, data, glossary, models


@st.cache_resource
def _live_aucs():
    return models.ensemble_aucs()


def render():
    c = content.load("results")
    st.title("Results")

    st.info(c["score_meaning"])
    glossary.render(st, "auc", "rank_agreement", "calibration", "mlp", "cnn", "multitask")

    st.markdown("## The models running on this site")
    aucs = _live_aucs()
    c1, c2 = st.columns(2)
    c1.metric("Data-only model (AUC)", f"{aucs['tabular_only']:.3f}",
              help="Tabular FlatMLP ensemble on 6 demographic features.")
    c2.metric("Photo + data model (AUC)", f"{aucs['multitask']:.3f}",
              help="Domain-invariant multi-task model: ConvNeXt photo trunk trained on "
                   "PetFinder + Taiwan photos, + adopt head.")
    st.caption(c["auc_caption"])

    st.markdown("## The research ladder (best configurations)")
    f = data.FINDINGS
    ladder = pd.DataFrame([
        {"Configuration": "Demographics only (deployed)", "AUC": f"{aucs['tabular_only']:.3f}",
         "Note": "What the columns alone can do"},
        {"Configuration": "Photo + data, multi-task (deployed)", "AUC": f"{aucs['multitask']:.3f}",
         "Note": "The model this site serves"},
        {"Configuration": "Photo + data, best research config", "AUC": f"{f['m06_multitask_auc']['value']}",
         "Note": "From our experiments"},
        {"Configuration": "Full feature set, ceiling", "AUC": f"{f['m06_ceiling_auc']['value']}",
         "Note": "From our experiments"},
    ])
    st.table(ladder)
    st.caption(c["ladder_caption"])

    st.markdown("## What we found")
    st.success(c["photos_win"].format(lift=f["m06_multitask_lift"]["value"]))
    st.success(c["one_lever"].format(caged=f["caged_rate_gap"]["value"]))
    st.info(c["older_dog_signal"])
    st.success(c["photo_count"])
    st.warning(c["tabular_ceiling"].format(ceiling=f["m05_accuracy_ceiling"]["value"]))
    st.warning(c["sentiment_null"])
    with st.expander("Where does the signal come from?"):
        st.markdown(c["signal_mechanism"])

    st.markdown("## Why this photo model")
    st.markdown(c["why_photo_model"])
    st.warning(c["photo_transfer"])
    st.info(c["photo_transfer_deep"])

    _render_calibration(c)

    st.markdown("## What the model is most confident about")
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

    st.markdown("## Is the score trustworthy? Calibration")
    st.markdown(c["calibration_intro"].format(n_test=n_test))

    rows = []
    for b in di["bins"]:
        if b["n"] == 0:
            continue
        rows.append({
            "Predicted range": f"{b['lo']:.0%}–{b['hi']:.0%}",
            "Dogs": b["n"],
            "Actually adopted": f"{b['actual_pct']:.1f}%",
            "Gap (pp)": f"{b['gap_pp']:+.1f}",
        })
    st.table(pd.DataFrame(rows))
    st.caption(c["calibration_caption"].format(
        ece=di["ece"], image_ece=models_cal["image_only"]["ece"]))

    st.markdown("## Confidence thresholds — a real policy lever")
    st.markdown(c["thresholds_intro"])
    trows = []
    for t in di["thresholds"]:
        label = "≥ 50% sure (all dogs)" if t["threshold"] == 0.5 else f"≥ {t['threshold']:.0%} sure"
        trows.append({
            "Act on dogs…": label,
            "Dogs covered": f"{t['coverage_pct']:.0f}%",
            "Accuracy": f"{t['accuracy_pct']:.0f}%" if t["accuracy_pct"] is not None else "—",
        })
    st.table(pd.DataFrame(trows))
    st.caption(c["thresholds_caption"])

    st.info(c["why_multitask"].format(ece=di["ece"]))
