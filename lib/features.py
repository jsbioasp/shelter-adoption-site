"""Turn human-friendly inputs into the SHARED_6 feature vector the models expect.

Two entry points:
  - derive_shared6(...)         from the Models UI form inputs
  - taiwan_row_to_shared6(row)  from a normalized Taiwan-dog record

SHARED_6 order (see lib.models.SHARED6_FEATURES):
    age_adult, is_young, is_mixed_breed, gender_male, gender_female, sterilized_yes
"""
from __future__ import annotations

import numpy as np


def derive_shared6(age_months: float, is_mixed_breed: bool, gender: str,
                   sterilized: bool) -> np.ndarray:
    """Build the SHARED_6 vector from Models-UI form inputs.

    Mirrors the feature derivations in _exp_common.load_dogs_with_cnn:
      age_adult = Age >= 12 months ; is_young = Age < 6 months.
    """
    age_adult = 1 if age_months >= 12 else 0
    is_young = 1 if age_months < 6 else 0
    gender_male = 1 if gender == "Male" else 0
    gender_female = 1 if gender == "Female" else 0
    return np.array([
        age_adult,
        is_young,
        1 if is_mixed_breed else 0,
        gender_male,
        gender_female,
        1 if sterilized else 0,
    ], dtype=np.float32)


def taiwan_row_to_shared6(row) -> np.ndarray:
    """Build SHARED_6 from a normalized Taiwan-dog record (see lib.data.normalize_taiwan).

    The Taiwan feed reports coarse age (ADULT / CHILD) rather than months, so:
      CHILD -> is_young=1, age_adult=0 ; ADULT -> age_adult=1, is_young=0.
    Sex is M/F (no neutered split); sterilization is T/F.
    """
    age_class = str(row.get("age_class", "")).upper()
    is_child = age_class == "CHILD"
    sex = str(row.get("sex", "")).upper()
    return np.array([
        0 if is_child else 1,                       # age_adult
        1 if is_child else 0,                        # is_young
        1 if row.get("is_mixed_breed") else 0,       # is_mixed_breed
        1 if sex == "M" else 0,                      # gender_male
        1 if sex == "F" else 0,                      # gender_female
        1 if str(row.get("sterilized", "")).upper() == "T" else 0,  # sterilized_yes
    ], dtype=np.float32)


def taiwan_frame_to_shared6(df) -> np.ndarray:
    """Vectorized SHARED_6 for a whole normalized Taiwan frame -> (N, 6) float32.

    Same rules as taiwan_row_to_shared6, applied column-wise so the data-only model
    can score every dog at once. Missing/unknown age counts as ADULT (matches the
    per-row helper's else-branch).
    """
    age = df["age_class"].astype(str).str.upper()
    is_child = (age == "CHILD")
    sex = df["sex"].astype(str).str.upper()
    ster = df["sterilized"].astype(str).str.upper()
    return np.column_stack([
        (~is_child).to_numpy(),                                   # age_adult
        is_child.to_numpy(),                                      # is_young
        (df["is_mixed_breed"].fillna(0).astype(int) != 0).to_numpy(),  # is_mixed_breed
        (sex == "M").to_numpy(),                                  # gender_male
        (sex == "F").to_numpy(),                                  # gender_female
        (ster == "T").to_numpy(),                                 # sterilized_yes
    ]).astype(np.float32)


def stratum_key(shared6: np.ndarray) -> str:
    """The 'y{young}_m{mixed}' stratum used in the rate-gap analysis."""
    is_young = int(shared6[1])
    is_mixed = int(shared6[2])
    return f"y{is_young}_m{is_mixed}"


def stratum_label(shared6: np.ndarray) -> str:
    """Plain-English / 白話 name for the stratum, e.g. 'young, mixed-breed'."""
    try:
        import streamlit as st
        lang = st.session_state.get("lang", "en")
    except Exception:
        lang = "en"
    if lang == "zh":
        young = "幼年" if int(shared6[1]) else "成年"
        breed = "米克斯" if int(shared6[2]) else "純種"
        return f"{young}、{breed}"
    young = "young" if int(shared6[1]) else "adult"
    breed = "mixed-breed" if int(shared6[2]) else "purebred"
    return f"{young}, {breed}"
