"""Plain-English definitions of the terms the site uses, in one place.

render(st, *keys) drops an expander defining just the terms a page actually
shows, so each page explains its own jargon and no term drifts between pages.
Keep every definition short and novice-friendly.
"""
from __future__ import annotations

TERMS = {
    "auc": "**AUC** — how well the model ranks a random adopted dog above a random "
           "not-yet-adopted one. 0.5 is a coin flip, 1.0 is perfect; our ~0.70 is fair, not great.",
    "rank_agreement": "**Rank agreement (Spearman)** — whether two rankings put things in the "
           "same order. 1.0 = identical order, 0 = unrelated. We use it to compare our shelter "
           "ranking against the government's published adoption rates.",
    "calibration": "**Calibration** — whether a score means what it says: if the model says 70%, "
           "do about 70% of those dogs actually get adopted? A calibrated score can be read as a "
           "real probability.",
    "mlp": "**MLP (multi-layer perceptron)** — a small neural network. Ours reads a dog's "
           "demographic facts (age, sex, breed, sterilization) and outputs an adoption-pace score.",
    "cnn": "**CNN (convolutional neural network)** — a network that reads images. Ours turns a "
           "listing photo into numbers, picking up cues like how young the dog looks.",
    "multitask": "**Multi-task** — training one network to predict two things at once so it learns "
           "better. Our photo model predicts adoption *and* 'is this a puppy?', which sharpens what "
           "it reads from the picture. (A separate, demographics-only model does the cross-country "
           "shelter ranking — photo style doesn't travel between countries, so photos are left out "
           "of that one.)",
    "strata": "**Strata** — the four demographic groups we compare within: young vs adult × "
           "purebred vs mixed-breed. Measuring an effect inside one group keeps the comparison "
           "like-for-like.",
}


def render(st, *keys, label="📖 Plain-English glossary"):
    """Drop an expander defining just the requested terms (in the order given)."""
    with st.expander(label):
        for k in keys:
            if k in TERMS:
                st.markdown("- " + TERMS[k])
