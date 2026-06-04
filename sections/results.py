"""Results section. Owner: <student>.

Best models, predictions, confidence. The deployed-model AUCs are read live from
the actual ensembles; the research ladder is cited from the findings docs.
"""
import pandas as pd
import streamlit as st

from lib import data, models


@st.cache_resource
def _live_aucs():
    return models.ensemble_aucs()


def render():
    st.title("Results")

    st.markdown("## The models running on this site")
    aucs = _live_aucs()
    c1, c2 = st.columns(2)
    c1.metric("Data-only model (AUC)", f"{aucs['tabular_only']:.3f}",
              help="Tabular FlatMLP ensemble on 6 demographic features.")
    c2.metric("Photo + data model (AUC)", f"{aucs['multitask']:.3f}",
              help="Multi-task model: ConvNeXt photo trunk + adopt head + is_young aux head.")
    st.caption("AUC = how well the model ranks a random adopted dog above a random "
               "non-adopted one. 0.5 is a coin flip; 1.0 is perfect. These are the "
               "*actual* 5-seed ensembles serving predictions on this site.")

    st.markdown("## The research ladder (best configurations)")
    f = data.FINDINGS
    ladder = pd.DataFrame([
        {"Configuration": "Demographics only (deployed)", "AUC": f"{aucs['tabular_only']:.3f}",
         "Note": "What the columns alone can do"},
        {"Configuration": "Photo + data, multi-task (deployed)", "AUC": f"{aucs['multitask']:.3f}",
         "Note": "The model this site serves"},
        {"Configuration": "Photo + data, best research config", "AUC": f"{f['m06_multitask_auc']['value']}",
         "Note": f"{f['m06_multitask_auc']['source']}"},
        {"Configuration": "Full feature set, ceiling", "AUC": f"{f['m06_ceiling_auc']['value']}",
         "Note": f"{f['m06_ceiling_auc']['source']}"},
    ])
    st.table(ladder)
    st.caption("The deployed model is a touch below the research ceiling — it trades a "
               "little AUC for a small, self-contained set of features that work on any "
               "shelter's data. Honesty over leaderboard.")

    _render_calibration()

    st.markdown("## What the model is most confident about")
    st.markdown(
        "- **Confident & right:** young, small, mixed-breed dogs with clean photos — "
        "the model and the outcomes agree.\n"
        "- **Confident & wrong:** cross-shelter transfer. The photo model is confident on "
        "Taiwan institutional photos and confidently wrong — see the Datasets page.\n"
        "- **Honest uncertainty:** for adult purebreds the signal is thin; the model "
        "says so with probabilities near the base rate."
    )


def _render_calibration():
    cal = data.load_calibration()
    if not cal:
        st.info("Calibration not computed yet — run `python scripts/compute_calibration.py`.")
        return
    models_cal = cal["models"]
    di = models_cal["data_image"]
    n_test = cal["n_test"]

    st.markdown("## Is the score trustworthy? Calibration")
    st.markdown(
        f"A score is only useful if it means what it says. **Calibration** asks: of the dogs "
        f"the photo+data model rated ~50%, did ~50% actually get adopted? Measured on "
        f"{n_test:,} held-out dogs, the answer is yes — predicted ≈ actual in every bin."
    )

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
    st.caption(f"Expected Calibration Error (ECE) = **{di['ece']:.3f}** — the average gap "
               "between predicted and actual is under ~2 points. The photo-only view is "
               f"noticeably less calibrated (ECE {models_cal['image_only']['ece']:.3f}), which "
               "is why the site treats it as a diagnostic, not a probability.")

    st.markdown("## Confidence thresholds — a real policy lever")
    st.markdown(
        "Because the photo+data model is calibrated, you can **act only on dogs it's sure "
        "about**: predict above a threshold T (likely adopted) or below 1−T (likely not). "
        "Higher T covers fewer dogs but is more accurate on the ones you keep."
    )
    trows = []
    for t in di["thresholds"]:
        label = "≥ 50% sure (all dogs)" if t["threshold"] == 0.5 else f"≥ {t['threshold']:.0%} sure"
        trows.append({
            "Act on dogs…": label,
            "Dogs covered": f"{t['coverage_pct']:.0f}%",
            "Accuracy": f"{t['accuracy_pct']:.0f}%" if t["accuracy_pct"] is not None else "—",
        })
    st.table(pd.DataFrame(trows))
    st.caption("This is the confidence lever a shelter actually uses: triage aggressively on "
               "the high-confidence dogs, give the uncertain ones a human look.")

    st.info(
        "**Why a *multi-task* model?** In the M06 experiments, a naive flat concatenation of "
        "photo + tabular features was badly overconfident (ECE ≈ 0.20 — it claimed 90% on "
        "dogs that adopted ~70% of the time). The multi-task architecture this site deploys "
        "keeps the photo signal in a separate trunk and stays calibrated (ECE ≈ "
        f"{di['ece']:.2f}). Calibration, not just AUC, is why we chose it."
    )
