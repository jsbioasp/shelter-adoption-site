"""Precompute the deployed ensembles' calibration on the held-out PetFinder test set.

BUILD-TIME script (depends on the M06 research data in modules/) — not imported by
the deployed site. Writes site/data/calibration.json, which the Results page renders
and the confidence labels read.

Three configs, matching the Models UI:
  - tabular_only : FlatMLP ensemble on SHARED_6           (expected: overconfident)
  - image_only   : MultiTask ensemble, zero tab vector
  - data_image   : MultiTask ensemble, real SHARED_6      (expected: well-calibrated)

For each: per-bin calibration (10 bins), ECE, and the confidence-threshold
coverage/accuracy table.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

SITE = Path(__file__).resolve().parent.parent
REPO = SITE.parent
sys.path.insert(0, str(SITE))

from lib import models  # vendored FlatMLP / MultiTaskMLP — reuse, don't redefine

import torch


def _flat_probs(ens, X_tab):
    Xt = ens["tab_scaler"].transform(X_tab).astype(np.float32)
    preds = np.zeros(len(X_tab))
    with torch.no_grad():
        for sd in ens["state_dicts"]:
            m = models.FlatMLP(n_in=ens["n_tab"]).to(models.DEVICE)
            m.load_state_dict(sd); m.eval()
            preds += torch.sigmoid(m(models._to_t(Xt))).cpu().numpy()
    return preds / len(ens["state_dicts"])


def _mt_probs(ens, X_img, X_tab):
    Xi = ens["img_scaler"].transform(X_img).astype(np.float32)
    Xt = ens["tab_scaler"].transform(X_tab).astype(np.float32)
    preds = np.zeros(len(X_img))
    with torch.no_grad():
        for sd in ens["state_dicts"]:
            m = models.MultiTaskMLP(n_img=ens["n_img"], n_tab=ens["n_tab"]).to(models.DEVICE)
            m.load_state_dict(sd); m.eval()
            adopt, _ = m(models._to_t(Xi), models._to_t(Xt))
            preds += torch.sigmoid(adopt).cpu().numpy()
    return preds / len(ens["state_dicts"])


def calibration(p, y, n_bins=10):
    edges = np.linspace(0, 1, n_bins + 1)
    bins, ece = [], 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & (p < hi) if hi < 1.0 else (p >= lo) & (p <= hi)
        n = int(m.sum())
        if n == 0:
            bins.append({"lo": round(lo, 1), "hi": round(hi, 1), "n": 0,
                         "actual_pct": None, "pred_pct": None, "gap_pp": None})
            continue
        actual = float(y[m].mean())
        pred = float(p[m].mean())
        ece += (n / len(p)) * abs(actual - pred)
        bins.append({"lo": round(lo, 1), "hi": round(hi, 1), "n": n,
                     "actual_pct": round(actual * 100, 1),
                     "pred_pct": round(pred * 100, 1),
                     "gap_pp": round((actual - pred) * 100, 1)})
    return bins, round(ece, 3)


def thresholds(p, y, ts=(0.5, 0.6, 0.7, 0.8)):
    conf = np.maximum(p, 1 - p)          # distance from the 0.5 boundary
    correct = (p >= 0.5).astype(int) == y
    rows = []
    for t in ts:
        cov = conf >= t
        n = int(cov.sum())
        rows.append({
            "threshold": t,
            "coverage_pct": round(100 * n / len(p), 0),
            "accuracy_pct": round(100 * float(correct[cov].mean()), 0) if n else None,
        })
    return rows


def main():
    # Research-only inputs: the held-out PetFinder test set + precomputed CNN
    # features. BUILD-TIME — needs the M06 research code/data under modules/,
    # which is NOT part of the deployed site repo. The site ships
    # data/calibration.json (this script's output), so running this is only
    # needed to *regenerate* calibration from the full course workspace.
    sys.path.insert(0, str(REPO / "modules/M06-vision-and-deployment/experiments"))
    try:
        from _exp_common import load_dogs_with_cnn, make_shared6
    except ModuleNotFoundError:
        sys.exit(
            "compute_calibration.py is a build-time script: it needs the M06 research "
            "data under modules/M06-vision-and-deployment/experiments/, which isn't part "
            "of this repo. data/calibration.json is already precomputed and shipped, so "
            "the deployed site does not need this script to run."
        )

    dogs, X_img, y, tr, te = load_dogs_with_cnn()
    S6 = make_shared6(dogs)
    yte = y[te]

    tab_ens = models._load_tabular_ensemble()
    mt_ens = models._load_multitask_ensemble()
    zero = np.zeros((len(te), mt_ens["n_tab"]), dtype=np.float32)

    p_tab = _flat_probs(tab_ens, S6[te])
    p_img = _mt_probs(mt_ens, X_img[te], zero)
    p_both = _mt_probs(mt_ens, X_img[te], S6[te])

    out = {"n_test": int(len(te)), "models": {}}
    for key, p in [("tabular_only", p_tab), ("image_only", p_img), ("data_image", p_both)]:
        bins, ece = calibration(p, yte)
        out["models"][key] = {
            "auc": round(float(roc_auc_score(yte, p)), 3),
            "ece": ece,
            "bins": bins,
            "thresholds": thresholds(p, yte),
        }
        print(f"{key:12} AUC={out['models'][key]['auc']}  ECE={ece}")

    (SITE / "data" / "calibration.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {SITE / 'data' / 'calibration.json'} (n_test={len(te)})")
    print("\nthreshold table (data_image):")
    for r in out["models"]["data_image"]["thresholds"]:
        print(f"  >= {r['threshold']:.0%}  coverage {r['coverage_pct']:.0f}%  "
              f"accuracy {r['accuracy_pct']:.0f}%")


if __name__ == "__main__":
    main()
