"""Data loading + the verified findings the site reports.

- normalize_taiwan(): shared by the ETL script and the loader so the snapshot
  schema is defined in exactly one place.
- load_taiwan_dogs(): reads the committed snapshot at data/taiwan_dogs.csv
  (refreshed by the scheduled GitHub Action).
- FINDINGS: the headline numbers, each with a source doc, so the Results and
  Datasets sections never hard-code an unsourced statistic.
"""
from __future__ import annotations

import io
import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TAIWAN_CSV = DATA_DIR / "taiwan_dogs.csv"
TAIWAN_META = DATA_DIR / "taiwan_meta.json"
CALIBRATION_JSON = DATA_DIR / "calibration.json"

# Live source — Taiwan Ministry of Agriculture open data (動物認領養).
# Verified 2026-06-02: returns animal_id / animal_kind / album_file / shelter_name ...
TAIWAN_SOURCE_JSON = (
    "https://data.moa.gov.tw/Service/OpenData/TransService.aspx"
    "?UnitId=QcbUEzN6E6DL&IsTransData=1"
)
TAIWAN_DATASET_PAGE = "https://data.gov.tw/en/datasets/85903"


# --------------------------------------------------------------------------
# Findings (each value carries the doc it came from)
# --------------------------------------------------------------------------

FINDINGS = {
    "m05_accuracy_ceiling": {
        "value": "~0.62 accuracy / +0.10 lift",
        "what": "What tabular PetFinder data alone can predict (the cascade is the deployment artifact).",
        "source": "M05-3 headline finding (CLAUDE.md M5 row).",
    },
    "m06_multitask_auc": {
        "value": 0.727,
        "what": "SHARED_6 + CNN photo features, multi-task model with is_young aux head (research best on the photo-having test subset).",
        "source": "M06-MULTITASK-FINDINGS.md (Session 34).",
    },
    "m06_ceiling_auc": {
        "value": 0.733,
        "what": "FULL_PLUS feature set + multi-task — the AUC ceiling reached in M06.",
        "source": "M06-MULTITASK-FINDINGS.md (Session 34).",
    },
    "m06_multitask_lift": {
        "value": "+0.032",
        "what": "AUC lift from adding CNN photo features over the tabular baseline.",
        "source": "M06-MULTITASK-FINDINGS.md.",
    },
    "taiwan_spearman": {
        "value": 0.927,
        "what": "Rank correlation between the model's per-shelter ranking and Taiwan's published adoption rates — the ranking transfers across countries even though absolute rates differ.",
        "source": "M05-CROSS-DATASET-INVESTIGATION-FINDINGS.md.",
    },
    "caged_rate_gap": {
        "value": "-16.9pp (95% CI [-26.3, -8.2], n=4,814)",
        "what": "Within young mixed-breed dogs, caged listing photos are associated with a 16.9-point drop in 30-day adoption rate.",
        "source": "trial/M07-advisory-tool/design.md (rate-gap analysis).",
    },
}


# --------------------------------------------------------------------------
# Taiwan snapshot
# --------------------------------------------------------------------------

# Columns the normalized snapshot exposes (what Discover Dogs displays + scores).
TAIWAN_COLUMNS = [
    "animal_id", "shelter_name", "area", "breed", "is_mixed_breed",
    "sex", "body_type", "color", "age_class", "sterilized",
    "photo_url", "found_place", "open_date", "shelter_address", "shelter_tel",
]


def normalize_taiwan(raw: pd.DataFrame) -> pd.DataFrame:
    """Filter the raw MOA feed to adoptable dogs-with-photos and tidy the columns.

    Shared by scripts/fetch_taiwan_dogs.py and (implicitly) the snapshot it writes,
    so the schema lives in one place.
    """
    df = raw.copy()
    df.columns = [c.strip().lstrip("﻿") for c in df.columns]

    # Dogs only, currently open for adoption, with a usable photo.
    df = df[df["animal_kind"].astype(str).str.strip() == "狗"]
    df = df[df["animal_status"].astype(str).str.strip() == "OPEN"]
    df = df[df["album_file"].astype(str).str.startswith("http")]

    variety = df["animal_Variety"].astype(str).str.strip()
    out = pd.DataFrame({
        "animal_id": df["animal_id"],
        "shelter_name": df["shelter_name"].astype(str).str.strip(),
        "area": df["animal_place"].astype(str).str.strip(),
        "breed": variety,
        "is_mixed_breed": variety.str.contains("混種").astype(int),
        "sex": df["animal_sex"].astype(str).str.strip(),
        "body_type": df["animal_bodytype"].astype(str).str.strip(),
        "color": df["animal_colour"].astype(str).str.strip(),
        "age_class": df["animal_age"].astype(str).str.strip(),
        "sterilized": df["animal_sterilization"].astype(str).str.strip(),
        "photo_url": df["album_file"].astype(str).str.strip(),
        "found_place": df["animal_foundplace"].astype(str).str.strip(),
        "open_date": df["animal_opendate"].astype(str).str.strip(),
        "shelter_address": df["shelter_address"].astype(str).str.strip(),
        "shelter_tel": df["shelter_tel"].astype(str).str.strip(),
    })
    return out[TAIWAN_COLUMNS].reset_index(drop=True)


def load_taiwan_dogs() -> pd.DataFrame:
    """Load the committed Taiwan snapshot. Empty frame (with columns) if missing."""
    if not TAIWAN_CSV.exists():
        return pd.DataFrame(columns=TAIWAN_COLUMNS)
    return pd.read_csv(TAIWAN_CSV, dtype={"animal_id": str})


def load_taiwan_meta() -> dict:
    """Snapshot metadata (fetched_at, n_dogs, source) written by the Action."""
    if not TAIWAN_META.exists():
        return {"fetched_at": "unknown", "n_dogs": 0, "source": TAIWAN_SOURCE_JSON}
    with open(TAIWAN_META, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_calibration() -> dict:
    """Per-model calibration (bins, ECE, threshold table) from compute_calibration.py.

    Empty dict if not computed yet — callers fall back to a sensible default.
    """
    if not CALIBRATION_JSON.exists():
        return {}
    with open(CALIBRATION_JSON, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=256)
def fetch_photo(url: str):
    """Download one listing photo -> PIL.Image, or None if it fails.

    Fetched server-side (not handed to the browser as a URL) so a dead photo
    degrades to None instead of a client-side broken-image error. Cached so a
    dog's photo is downloaded at most once per process.
    """
    import requests
    from PIL import Image
    if not isinstance(url, str) or not url.startswith("http"):
        return None
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
    except requests.exceptions.SSLError:
        try:
            r = requests.get(url, timeout=15, verify=False)
            r.raise_for_status()
        except Exception:
            return None
    except Exception:
        return None
    try:
        return Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception:
        return None
