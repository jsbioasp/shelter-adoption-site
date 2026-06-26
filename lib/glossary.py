"""Plain-English definitions of the terms the site uses, in one place.

render(st, *keys) shows, inline at the top of a page, just the terms that page
actually uses, so each page explains its own jargon and no term drifts between pages.
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
    "ece": "**ECE (expected calibration error)** — how far a score's confidence sits from reality, "
           "on average. If the model says 70% but those dogs adopt 65% of the time, ECE sums up that "
           "5-point gap. Lower is better; ~0.05 means predictions land within about 5 points.",
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
    "pp": "**pp (percentage points)** — the plain gap between two percentages. From a 30% adoption "
          "rate to 47% is a rise of 17 points (17pp); we say 'points' so it isn't confused with a "
          "'percent increase'.",
}


def render(st, *keys, label="📖 Plain-English glossary"):
    """Render the requested terms (in the order given) inline at the top of a page.

    Shown directly on the page, not tucked behind a click — define the jargon
    before the reader hits it.
    """
    lines = [f"- {TERMS[k]}" for k in keys if k in TERMS]
    if lines:
        st.markdown(f"**{label}**\n\n" + "\n".join(lines))
