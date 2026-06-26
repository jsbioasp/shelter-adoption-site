"""Model loading + scoring for the shelter-ML site.

Everything here is self-contained so the app deploys to Streamlit Cloud without
depending on the research code in `modules/` or `trial/`. The two model classes
are vendored copies of the architectures the ensembles were trained with
(`modules/M06-vision-and-deployment/experiments/_exp_common.py`); the state-dict
keys must match exactly or `load_state_dict` fails.

Three scoring modes match the wireframe's "Models UI":
  - score_data_only(shared6)        -> tabular FlatMLP ensemble   (m06_tabular_only.pkl)
  - score_image_only(pil)           -> MultiTask ensemble, zero tab vector
  - score_data_and_image(pil, s6)   -> MultiTask ensemble, real SHARED_6 tab vector

The image modes run a ConvNeXt-Tiny encoder (768-dim features) on CPU. That's the
same encoder that produced `petfinder_cnn_features.csv` in M06.
"""
from __future__ import annotations

import pickle
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# Streamlit Community Cloud is CPU-only. Detect a GPU if running elsewhere.
DEVICE = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)

# SHARED_6 feature order — must match make_shared6() in _exp_common.py.
SHARED6_FEATURES = [
    "age_adult", "is_young", "is_mixed_breed",
    "gender_male", "gender_female", "sterilized_yes",
]


# --------------------------------------------------------------------------
# Vendored model architectures (must match the trained state dicts)
# --------------------------------------------------------------------------

class FlatMLP(nn.Module):
    """Tabular-only model. State-dict keys: net.0 / net.3 / net.6."""

    def __init__(self, n_in: int, hidden=(64, 32), dropout=0.3):
        super().__init__()
        layers, prev = [], n_in
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.Dropout(dropout)]
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x).squeeze(-1)


class MultiTaskMLP(nn.Module):
    """Photo trunk + adopt head (+ is_young aux head).

    State-dict keys: trunk.0 / trunk.3 / aux_head / adopt_head.0 / adopt_head.3.
    The adopt head concatenates the photo trunk output with the tab vector.
    """

    def __init__(self, n_img: int, n_tab: int, trunk=(64, 32), adopt_head=(16,), dropout=0.3):
        super().__init__()
        layers, prev = [], n_img
        for h in trunk:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.Dropout(dropout)]
            prev = h
        self.trunk = nn.Sequential(*layers)
        trunk_dim = prev
        self.aux_head = nn.Linear(trunk_dim, 1)
        layers, prev = [], trunk_dim + n_tab
        for h in adopt_head:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.Dropout(dropout)]
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.adopt_head = nn.Sequential(*layers)

    def forward(self, x_img, x_tab):
        z = self.trunk(x_img)
        aux_logit = self.aux_head(z).squeeze(-1)
        adopt_logit = self.adopt_head(torch.cat([z, x_tab], dim=1)).squeeze(-1)
        return adopt_logit, aux_logit


def _to_t(arr) -> torch.Tensor:
    return torch.tensor(arr, dtype=torch.float32, device=DEVICE)


# --------------------------------------------------------------------------
# Ensemble loading (cached — load once per process)
# --------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_tabular_ensemble() -> dict:
    with open(MODELS_DIR / "m06_tabular_only.pkl", "rb") as f:
        return pickle.load(f)


@lru_cache(maxsize=1)
def _load_multitask_ensemble() -> dict:
    # Deployed photo model = bridge_YU: same MultiTaskMLP, but its ConvNeXt trunk was
    # pretrained across BOTH PetFinder and Taiwan COA photos (domain-invariant), so it
    # reads the dog rather than the photographer's style. Sharper ranker (AUC ~0.72),
    # slightly looser calibration (ECE ~0.05) — see content/results.md "why_photo_model".
    with open(MODELS_DIR / "m06_bridge_yu.pkl", "rb") as f:
        return pickle.load(f)


@lru_cache(maxsize=1)
def _load_photo_encoder():
    """ConvNeXt-Tiny with the classifier truncated to its 768-dim feature output.

    Weights download from torchvision on first call (~110 MB) — slow only on cold
    start. The same encoder produced M06's precomputed CNN features.
    """
    from torchvision import models

    weights = models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1
    backbone = models.convnext_tiny(weights=weights)
    # Keep LayerNorm2d + Flatten, drop the final Linear -> 768-dim features.
    backbone.classifier = nn.Sequential(backbone.classifier[0], backbone.classifier[1])
    backbone.eval().to(DEVICE)
    for p in backbone.parameters():
        p.requires_grad = False
    return backbone, weights.transforms()


def encode_photo(pil_image) -> np.ndarray:
    """One PIL image -> 768-dim ConvNeXt feature vector."""
    backbone, preprocess = _load_photo_encoder()
    t = preprocess(pil_image.convert("RGB")).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        return backbone(t).cpu().numpy().reshape(1, -1)


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------

def _seed_probs_flat(ens: dict, X_tab: np.ndarray) -> np.ndarray:
    """Per-seed P(adopt) from the FlatMLP ensemble (length = #seeds)."""
    Xt = ens["tab_scaler"].transform(X_tab).astype(np.float32)
    probs = []
    with torch.no_grad():
        for sd in ens["state_dicts"]:
            mdl = FlatMLP(n_in=ens["n_tab"]).to(DEVICE)
            mdl.load_state_dict(sd)
            mdl.eval()
            logit = mdl(_to_t(Xt))
            probs.append(float(torch.sigmoid(logit).cpu().numpy().squeeze()))
    return np.array(probs)


def _seed_probs_multitask(ens: dict, X_img: np.ndarray, X_tab: np.ndarray) -> np.ndarray:
    """Per-seed adopt-head P(adopt) from the MultiTaskMLP ensemble (length = #seeds)."""
    Xi = ens["img_scaler"].transform(X_img).astype(np.float32)
    Xt = ens["tab_scaler"].transform(X_tab).astype(np.float32)
    probs = []
    with torch.no_grad():
        for sd in ens["state_dicts"]:
            mdl = MultiTaskMLP(n_img=ens["n_img"], n_tab=ens["n_tab"]).to(DEVICE)
            mdl.load_state_dict(sd)
            mdl.eval()
            adopt_logit, _ = mdl(_to_t(Xi), _to_t(Xt))
            probs.append(float(torch.sigmoid(adopt_logit).cpu().numpy().squeeze()))
    return np.array(probs)


# Confidence = the calibrated probability's distance from the 0.5 decision boundary,
# mapped to the confidence-threshold table (how accurate the model is among dogs it's
# this sure about). Meaningful ONLY because the data_image model is calibrated
# (ECE ~0.05) — see the Results page / compute_calibration.py.
def confidence_from_prob(p: float, model: str = "data_image") -> dict:
    """Map a calibrated probability to a confidence read.

    Returns {label, conf (max(p,1-p)), accuracy_pct} where accuracy_pct is
    the model's measured accuracy among dogs at least this confident (from the
    threshold table). Falls back to label-only if calibration data is missing.
    """
    from lib import data
    conf = max(p, 1.0 - p)
    if conf >= 0.8:
        label = "High"
    elif conf >= 0.7:
        label = "Good"
    elif conf >= 0.6:
        label = "Moderate"
    else:
        label = "Low"

    accuracy_pct = None
    cal = data.load_calibration().get("models", {}).get(model, {})
    # Find the highest threshold this prediction clears; report its measured accuracy.
    for row in sorted(cal.get("thresholds", []), key=lambda r: r["threshold"], reverse=True):
        if conf >= row["threshold"] and row.get("accuracy_pct") is not None:
            accuracy_pct = row["accuracy_pct"]
            break
    return {"label": label, "conf": conf, "accuracy_pct": accuracy_pct}


def score_data_only(shared6: np.ndarray) -> float:
    """Mean P(adopt within 30 days) from SHARED_6 demographics alone."""
    mean, _ = score_data_only_ci(shared6)
    return mean


def score_data_only_ci(shared6: np.ndarray) -> tuple[float, float]:
    """(mean, std) P(adopt) from demographics alone, across the seed ensemble."""
    ens = _load_tabular_ensemble()
    p = _seed_probs_flat(ens, np.asarray(shared6, dtype=np.float32).reshape(1, -1))
    return float(p.mean()), float(p.std())


def score_data_only_batch(shared6_matrix) -> np.ndarray:
    """Mean P(adopt) for MANY dogs at once from demographics alone.

    shared6_matrix is (N, 6); returns an (N,) array of mean P(adopt) across the
    seed ensemble. Tabular-only, so it's fast enough to score the whole Taiwan
    snapshot live (no photo encoding) — that's what makes data-score search
    population-wide.
    """
    ens = _load_tabular_ensemble()
    X = np.asarray(shared6_matrix, dtype=np.float32).reshape(-1, ens["n_tab"])
    Xt = ens["tab_scaler"].transform(X).astype(np.float32)
    acc = np.zeros(len(X), dtype=np.float64)
    with torch.no_grad():
        Xt_t = _to_t(Xt)
        for sd in ens["state_dicts"]:
            mdl = FlatMLP(n_in=ens["n_tab"]).to(DEVICE)
            mdl.load_state_dict(sd)
            mdl.eval()
            acc += torch.sigmoid(mdl(Xt_t)).cpu().numpy().reshape(-1)
    return acc / len(ens["state_dicts"])


def score_image_only(pil_image) -> float:
    """Mean P(adopt) from the photo alone (zero demographic vector)."""
    mean, _ = score_image_only_ci(pil_image)
    return mean


def score_image_only_ci(pil_image) -> tuple[float, float]:
    """(mean, std) P(adopt) from the photo alone — the photo-axis-only view."""
    ens = _load_multitask_ensemble()
    cnn = encode_photo(pil_image)
    tab = np.zeros((1, ens["n_tab"]), dtype=np.float32)
    p = _seed_probs_multitask(ens, cnn, tab)
    return float(p.mean()), float(p.std())


def score_data_and_image(pil_image, shared6: np.ndarray) -> float:
    """Mean P(adopt) from photo + demographics — the full M06 multi-task model."""
    mean, _ = score_data_and_image_ci(pil_image, shared6)
    return mean


def score_data_and_image_ci(pil_image, shared6: np.ndarray) -> tuple[float, float]:
    """(mean, std) P(adopt) from photo + demographics — the best model + its confidence."""
    ens = _load_multitask_ensemble()
    cnn = encode_photo(pil_image)
    tab = np.asarray(shared6, dtype=np.float32).reshape(1, -1)
    p = _seed_probs_multitask(ens, cnn, tab)
    return float(p.mean()), float(p.std())


def score_photo_both_ci(pil_image, shared6: np.ndarray) -> dict:
    """One photo encode -> both (mean, std) for image+data and image-only.

    Encodes the photo once and reuses the features for both heads — half the work
    of calling the two scorers separately. Used by Discover Dogs per card.
    """
    ens = _load_multitask_ensemble()
    cnn = encode_photo(pil_image)
    tab = np.asarray(shared6, dtype=np.float32).reshape(1, -1)
    zero = np.zeros((1, ens["n_tab"]), dtype=np.float32)
    p_both = _seed_probs_multitask(ens, cnn, tab)
    p_img = _seed_probs_multitask(ens, cnn, zero)
    return {
        "data_image": (float(p_both.mean()), float(p_both.std())),
        "image_only": (float(p_img.mean()), float(p_img.std())),
    }


def ensemble_aucs() -> dict:
    """Reported test AUCs for the two ensembles (for the Results section)."""
    return {
        "tabular_only": float(np.mean(_load_tabular_ensemble()["aucs"])),
        "multitask": float(np.mean(_load_multitask_ensemble()["aucs"])),
    }
