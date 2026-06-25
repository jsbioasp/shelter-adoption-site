"""Discover Dogs section — browse live Taiwan adoptable dogs. Owner: <student>.

Page-level prose lives in content/discover.md (edit it there). The per-dog card
and dialog text is data-driven, so it stays here.

Shows 10 random adoptable dogs (shuffle for more), each scored from its actual
listing photo two ways:
  - Photo + data : the full multi-task model (our best) — calibrated, continuous
  - Photo only   : the same model with demographics zeroed — a diagnostic

Each photo+data score shows BOTH a raw confidence (how far from a coin-flip) and
the model's measured accuracy at that confidence on the held-out test set. Click a
dog for full stats and shelter contact info.

Why photo-score instead of demographics: the data-only model sees only ~16
demographic buckets, so it can't rank individuals. The photo is what varies per
dog (see Results). Only the shown dogs are scored (cached), so the page stays fast.
"""
import urllib.parse
from functools import lru_cache

import streamlit as st
from PIL import Image, ImageDraw

from lib import content, data, features, glossary, models


@lru_cache(maxsize=1)
def _placeholder():
    """A locally-rendered 'no photo' image. Built in-process so the browser never
    fetches an external placeholder URL (those error out client-side)."""
    img = Image.new("RGB", (400, 400), (235, 235, 235))
    d = ImageDraw.Draw(img)
    bbox = d.textbbox((0, 0), "no photo")
    d.text(((400 - (bbox[2] - bbox[0])) / 2, (400 - (bbox[3] - bbox[1])) / 2),
           "no photo", fill=(140, 140, 140))
    return img


@st.cache_data(show_spinner=False)
def _score_dog(animal_id: str, photo_url: str, s6_tuple: tuple):
    """Score a dog three ways. Data-only needs no photo, so it's always available;
    photo-only and photo+data are added when the listing photo loads. Cached per dog."""
    import numpy as np
    s6 = np.array(s6_tuple, dtype="float32")
    out = {"data_only": models.score_data_only(s6)}
    img = data.fetch_photo(photo_url)
    if img is None:
        out["ok"] = False
        return out
    both = models.score_photo_both_ci(img, s6)
    out.update({"ok": True, **both})
    return out


def _clean(val, dash="—"):
    s = str(val).strip()
    return dash if s.lower() in ("nan", "", "none") else s


def _conf_and_acc(p, model="data_image"):
    """(raw confidence, test-set accuracy %) for a calibrated probability."""
    c = models.confidence_from_prob(p, model=model)
    return c["conf"], c["accuracy_pct"]


@st.dialog("Dog details & shelter contact")
def _details_dialog(row, scores, n_test):
    img = data.fetch_photo(row["photo_url"]) if scores["ok"] else None
    st.image(img if img is not None else _placeholder(), width=260)
    st.markdown(f"### {_clean(row['breed'])}")

    c1, c2 = st.columns(2)
    c1.markdown(
        f"- **Sex:** {_clean(row['sex'])}\n"
        f"- **Age:** {_clean(row['age_class']).title()}\n"
        f"- **Body type:** {_clean(row['body_type']).title()}\n"
        f"- **Color:** {_clean(row['color'])}"
    )
    c2.markdown(
        f"- **Sterilized:** {_clean(row['sterilized'])}\n"
        f"- **Found at:** {_clean(row['found_place'])}\n"
        f"- **Listed:** {_clean(row['open_date'])}\n"
        f"- **Animal ID:** {_clean(row['animal_id'])}"
    )

    st.markdown("#### Model read")
    p_data = scores["data_only"]
    if scores["ok"]:
        p_both = scores["data_image"][0]
        p_img = scores["image_only"][0]
        conf, acc = _conf_and_acc(p_both)
        st.markdown(
            f"- **Photo + data:** {p_both:.0%} adoption pace (50% = average) · raw confidence "
            f"{conf:.0%} · **~{acc:.0f}% accurate on the held-out test set** (n={n_test:,})\n"
            f"- **Photo only (diagnostic):** {p_img:.0%} — uncalibrated; what the picture "
            "suggests without demographics\n"
            f"- **Data only:** {p_data:.0%} — the demographics-only baseline (identical for "
            "dogs with the same age/sex/breed/sterilization)"
        )
    else:
        st.markdown(
            f"- **Data only:** {p_data:.0%} — the demographics-only baseline.\n"
            "- *Photo unavailable, so the photo-based reads can't be computed for this dog.*"
        )

    st.caption(content.load("discover")["model_honesty"])

    st.markdown("#### Contact the shelter")
    addr = _clean(row["shelter_address"])
    tel = _clean(row["shelter_tel"])
    shelter_name = _clean(row["shelter_name"])
    st.markdown(f"**{shelter_name}**")
    if addr != "—":
        maps = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(addr)
        st.markdown(f"📍 {addr} — [open in Maps]({maps})")
    if tel != "—":
        st.markdown(f"📞 [{tel}](tel:{tel.replace(' ', '')})")
    if shelter_name != "—":
        search = "https://www.google.com/search?q=" + urllib.parse.quote(shelter_name)
        st.markdown(f"🔎 [Find this shelter online]({search}) — for its website, "
                    "contact form, or email")
    st.caption(content.load("discover")["contact_caption"])
    st.info(f"When you contact the shelter, mention **animal ID {_clean(row['animal_id'])}**.")


def _card(row, n_test):
    c1, c2 = st.columns([1, 2])
    scores = _score_dog(str(row["animal_id"]), row["photo_url"],
                        tuple(features.taiwan_row_to_shared6(row).tolist()))
    with c1:
        img = data.fetch_photo(row["photo_url"]) if scores["ok"] else None
        st.image(img if img is not None else _placeholder(), width=180)
    with c2:
        st.markdown(f"**{_clean(row['breed'])}** · {_clean(row['sex'])} · "
                    f"{_clean(row['age_class']).title()}")
        st.markdown(f"📍 {_clean(row['shelter_name'])} ({_clean(row['area'])})")
        if scores["ok"]:
            p_both = scores["data_image"][0]
            conf, acc = _conf_and_acc(p_both)
            st.progress(min(max(p_both, 0.0), 1.0),
                        text=f"Photo + data: {p_both:.0%} · confidence {conf:.0%} · "
                             f"~{acc:.0f}% test accuracy")
            st.progress(min(max(scores["image_only"][0], 0.0), 1.0),
                        text=f"Photo only: {scores['image_only'][0]:.0%} · "
                             "diagnostic (uncalibrated)")
        else:
            st.caption("📷 Photo unavailable — showing the demographics-only score below.")
        st.progress(min(max(scores["data_only"], 0.0), 1.0),
                    text=f"Data only: {scores['data_only']:.0%} · demographics baseline")
        if st.button("🔍 Details & contact", key=f"details_{row['animal_id']}"):
            _details_dialog(row, scores, n_test)


# Sort options. Value is (column, ascending) or None for random.
# "score_data" sorts the WHOLE filtered population (data score is known for every
# dog). "data_image"/"image_only" sort only the shown set (photo scores are computed
# for the dogs on screen, not the whole population).
SORTS = {
    "Random": None,
    "Data score — lowest first (needs help most)": ("score_data", True),
    "Data score — highest first": ("score_data", False),
    "Photo + data — lowest first (shown set)": ("data_image", True),
    "Photo + data — highest first (shown set)": ("data_image", False),
    "Photo only — lowest first (shown set)": ("image_only", True),
    "Photo only — highest first (shown set)": ("image_only", False),
}


@st.cache_data(show_spinner="Scoring every dog by demographics…")
def _scored_frame(fetched_at: str, n: int):
    """Load the snapshot and add a `score_data` column for ALL dogs (cheap, no photos).
    Cached on the snapshot identity so it computes once per refresh."""
    df = data.load_taiwan_dogs()
    if len(df):
        df = df.copy()
        df["score_data"] = models.score_data_only_batch(features.taiwan_frame_to_shared6(df))
    return df


def _filter(df, shelter, sex, breed, age, ster, body, score_lo, score_hi):
    view = df
    if shelter != "All shelters":
        view = view[view["shelter_name"] == shelter]
    if sex != "Any":
        view = view[view["sex"] == sex]
    if breed != "Any":
        view = view[view["is_mixed_breed"] == (1 if breed == "Mixed-breed" else 0)]
    if age != "Any":
        view = view[view["age_class"] == age]
    if ster != "Any":
        view = view[view["sterilized"] == {"Yes": "T", "No": "F", "Unknown": "N"}[ster]]
    if body != "Any":
        view = view[view["body_type"] == body]
    return view[(view["score_data"] >= score_lo) & (view["score_data"] <= score_hi)]


def render():
    c = content.load("discover")
    st.title("Discover Dogs")
    meta = data.load_taiwan_meta()
    n_test = data.load_calibration().get("n_test", 0)
    df = _scored_frame(meta.get("fetched_at", "unknown"), meta.get("n_dogs", 0))

    if len(df) == 0:
        st.warning(c["no_snapshot"])
        return

    st.caption(f"Live from Taiwan MOA open data · {meta.get('n_dogs', len(df)):,} dogs · "
               f"{meta.get('n_shelters', df['shelter_name'].nunique())} shelters · "
               f"refreshed {meta.get('fetched_at', 'unknown')} "
               f"([source]({data.TAIWAN_DATASET_PAGE}))")

    glossary.render(st, "calibration")

    with st.sidebar:
        st.markdown("### Search dogs")
        shelter = st.selectbox("Shelter", ["All shelters"] + sorted(df["shelter_name"].unique()))
        sex = st.radio("Sex", ["Any", "F", "M"], horizontal=True)
        breed = st.radio("Breed", ["Any", "Mixed-breed", "Purebred"], horizontal=True)
        age = st.radio("Age", ["Any", "CHILD", "ADULT"], horizontal=True)
        ster = st.radio("Sterilized", ["Any", "Yes", "No", "Unknown"], horizontal=True)
        body = st.selectbox("Body type", ["Any"] + sorted(df["body_type"].dropna().unique()))
        lo, hi = st.slider("Data score — adoption pace %", 0, 100, (0, 100), step=5,
                           help="The demographics-only adoption-pace score (50% = average). "
                                "Filters every dog.")
        sort_label = st.selectbox("Sort by", list(SORTS.keys()))
        n_show = st.slider("How many to show", 3, 24, 10, step=1)
        shuffled = st.button("🎲 Shuffle", use_container_width=True)

    view = _filter(df, shelter, sex, breed, age, ster, body, lo / 100, hi / 100)
    sort = SORTS[sort_label]
    data_sort = sort is not None and sort[0] == "score_data"

    if len(view) == 0:
        st.warning(c["no_match"])
        return

    # Data-score sorts are deterministic over the whole filtered set → just take the
    # top N. Random and photo-based sorts draw a sample (persisted so clicking a dog
    # doesn't reshuffle); photo-based sorts then reorder that shown sample below.
    if data_sort:
        col, asc = sort
        shown = view.sort_values(col, ascending=asc).head(n_show)
    else:
        sig = (shelter, sex, breed, age, ster, body, lo, hi, n_show, sort_label)
        if (shuffled or st.session_state.get("just_navigated")
                or st.session_state.get("disc_sig") != sig
                or "disc_ids" not in st.session_state):
            pool = view if len(view) <= n_show else view.sample(n_show)
            st.session_state["disc_ids"] = pool["animal_id"].astype(str).tolist()
            st.session_state["disc_sig"] = sig
        ids = set(st.session_state["disc_ids"])
        shown = view[view["animal_id"].astype(str).isin(ids)]

    st.markdown(c["results_intro"].format(n_view=len(view), lo=lo, hi=hi, n_shown=len(shown)))
    st.caption(c["model_honesty"])

    rows = [row for _, row in shown.iterrows()]
    with st.spinner(f"Downloading + scoring {len(rows)} photos…"):
        # Score the shown dogs' photos (cached per dog) so photo-based sorts can order them.
        if sort is not None and sort[0] in ("data_image", "image_only"):
            col, asc = sort

            def _key(row):
                s = _score_dog(str(row["animal_id"]), row["photo_url"],
                               tuple(features.taiwan_row_to_shared6(row).tolist()))
                if not s.get("ok"):
                    return (1, 0.0)            # photo-less dogs sort to the end
                return (0, s[col][0] if asc else -s[col][0])
            rows.sort(key=_key)
        for row in rows:
            _card(row, n_test)
            st.divider()
