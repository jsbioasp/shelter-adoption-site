"""Discover Dogs section — browse live Taiwan adoptable dogs. Owner: <student>.

Page prose lives in content/<lang>/discover.md; the data-driven card/dialog chrome
comes from lib.i18n. Filter widgets keep their data/logic VALUES (F/M, CHILD/ADULT,
the SORTS keys) and translate only their display via format_func.
"""
import urllib.parse
from functools import lru_cache

import streamlit as st
from PIL import Image, ImageDraw

from lib import content, data, features, glossary, models
from lib.i18n import t


@lru_cache(maxsize=2)
def _placeholder(text="no photo"):
    """A locally-rendered 'no photo' image (cached per language text)."""
    img = Image.new("RGB", (400, 400), (235, 235, 235))
    d = ImageDraw.Draw(img)
    bbox = d.textbbox((0, 0), text)
    d.text(((400 - (bbox[2] - bbox[0])) / 2, (400 - (bbox[3] - bbox[1])) / 2),
           text, fill=(140, 140, 140))
    return img


@st.cache_data(show_spinner=False)
def _score_dog(animal_id, photo_url, s6_tuple):
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


def _sex_disp(v):
    return {"F": t("disc_sex_f"), "M": t("disc_sex_m")}.get(_clean(v), _clean(v))


def _age_disp(v):
    return {"CHILD": t("disc_child"), "ADULT": t("disc_adult")}.get(str(v).strip().upper(), _clean(v).title())


def _ster_disp(v):
    return {"T": t("disc_yes"), "F": t("disc_no"), "N": t("disc_unknown")}.get(_clean(v).upper(), _clean(v))


def _conf_and_acc(p, model="data_image"):
    c = models.confidence_from_prob(p, model=model)
    return c["conf"], c["accuracy_pct"]


@st.dialog("狗狗詳情與聯絡 · Dog details")
def _details_dialog(row, scores, n_test):
    img = data.fetch_photo(row["photo_url"]) if scores["ok"] else None
    st.image(img if img is not None else _placeholder(t("disc_no_photo")), width=260)
    st.markdown(f"### {_clean(row['breed'])}")

    c1, c2 = st.columns(2)
    c1.markdown(
        f"- **{t('disc_d_sex')}:** {_sex_disp(row['sex'])}\n"
        f"- **{t('disc_d_age')}:** {_age_disp(row['age_class'])}\n"
        f"- **{t('disc_d_body')}:** {_clean(row['body_type']).title()}\n"
        f"- **{t('disc_d_color')}:** {_clean(row['color'])}"
    )
    c2.markdown(
        f"- **{t('disc_d_ster')}:** {_ster_disp(row['sterilized'])}\n"
        f"- **{t('disc_d_found')}:** {_clean(row['found_place'])}\n"
        f"- **{t('disc_d_listed')}:** {_clean(row['open_date'])}\n"
        f"- **{t('disc_d_id')}:** {_clean(row['animal_id'])}"
    )

    st.markdown("#### " + t("disc_d_model_read"))
    p_data = scores["data_only"]
    if scores["ok"]:
        p_both = scores["data_image"][0]
        p_img = scores["image_only"][0]
        conf, acc = _conf_and_acc(p_both)
        st.markdown(
            "- " + t("disc_d_both").format(p=f"{p_both:.0%}", conf=f"{conf:.0%}", acc=f"{acc:.0f}", n=f"{n_test:,}") + "\n"
            "- " + t("disc_d_img").format(p=f"{p_img:.0%}") + "\n"
            "- " + t("disc_d_data").format(p=f"{p_data:.0%}")
        )
    else:
        st.markdown(
            "- " + t("disc_d_data_short").format(p=f"{p_data:.0%}") + "\n"
            "- " + t("disc_d_photo_unavail")
        )

    st.caption(content.load("discover")["model_honesty"])

    st.markdown("#### " + t("disc_d_contact"))
    addr = _clean(row["shelter_address"])
    tel = _clean(row["shelter_tel"])
    shelter_name = _clean(row["shelter_name"])
    st.markdown(f"**{shelter_name}**")
    contact = []
    if addr != "—":
        maps = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(addr)
        contact.append(f"- {addr} — [{t('disc_d_maps')}]({maps})")
    if tel != "—":
        contact.append(f"- [{tel}](tel:{tel.replace(' ', '')})")
    if shelter_name != "—":
        search = "https://www.google.com/search?q=" + urllib.parse.quote(shelter_name)
        contact.append(f"- [{t('disc_d_find_online')}]({search}){t('disc_d_find_suffix')}")
    if contact:
        st.markdown("\n".join(contact))
    st.caption(content.load("discover")["contact_caption"])
    st.info(t("disc_d_mention").format(id=_clean(row["animal_id"])))


def _card(row, n_test):
    c1, c2 = st.columns([1, 2])
    scores = _score_dog(str(row["animal_id"]), row["photo_url"],
                        tuple(features.taiwan_row_to_shared6(row).tolist()))
    with c1:
        img = data.fetch_photo(row["photo_url"]) if scores["ok"] else None
        st.image(img if img is not None else _placeholder(t("disc_no_photo")), width=180)
    with c2:
        st.markdown(f"**{_clean(row['breed'])}** · {_sex_disp(row['sex'])} · {_age_disp(row['age_class'])}")
        st.markdown(f"{_clean(row['shelter_name'])} ({_clean(row['area'])})")
        if scores["ok"]:
            p_both = scores["data_image"][0]
            conf, acc = _conf_and_acc(p_both)
            st.progress(min(max(p_both, 0.0), 1.0),
                        text=t("disc_card_both").format(p=f"{p_both:.0%}", conf=f"{conf:.0%}", acc=f"{acc:.0f}"))
            st.progress(min(max(scores["image_only"][0], 0.0), 1.0),
                        text=t("disc_card_img").format(p=f"{scores['image_only'][0]:.0%}"))
        else:
            st.caption(t("disc_card_photo_unavail"))
        st.progress(min(max(scores["data_only"], 0.0), 1.0),
                    text=t("disc_card_data").format(p=f"{scores['data_only']:.0%}"))
        if st.button(t("disc_details_btn"), key=f"details_{row['animal_id']}"):
            _details_dialog(row, scores, n_test)


SORTS = {
    "Random": None,
    "Data score — lowest first (needs help most)": ("score_data", True),
    "Data score — highest first": ("score_data", False),
    "Photo + data — lowest first (shown set)": ("data_image", True),
    "Photo + data — highest first (shown set)": ("data_image", False),
    "Photo only — lowest first (shown set)": ("image_only", True),
    "Photo only — highest first (shown set)": ("image_only", False),
}

_SORT_KEYS = {
    "Random": "disc_sort_random",
    "Data score — lowest first (needs help most)": "disc_sort_data_low",
    "Data score — highest first": "disc_sort_data_high",
    "Photo + data — lowest first (shown set)": "disc_sort_both_low",
    "Photo + data — highest first (shown set)": "disc_sort_both_high",
    "Photo only — lowest first (shown set)": "disc_sort_img_low",
    "Photo only — highest first (shown set)": "disc_sort_img_high",
}


@st.cache_data(show_spinner="Scoring every dog by demographics…")
def _scored_frame(fetched_at, n):
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
    st.title(t("nav_discover"))
    meta = data.load_taiwan_meta()
    n_test = data.load_calibration().get("n_test", 0)
    df = _scored_frame(meta.get("fetched_at", "unknown"), meta.get("n_dogs", 0))

    if len(df) == 0:
        st.warning(c["no_snapshot"])
        return

    st.caption(t("disc_live_fmt").format(
        n=f"{meta.get('n_dogs', len(df)):,}",
        s=meta.get("n_shelters", df["shelter_name"].nunique()),
        d=meta.get("fetched_at", "unknown"), src=data.TAIWAN_DATASET_PAGE))

    glossary.render(st, "calibration")

    with st.sidebar:
        st.markdown("### " + t("disc_search"))
        shelter = st.selectbox(
            t("disc_shelter"), ["All shelters"] + sorted(df["shelter_name"].unique()),
            format_func=lambda v: t("disc_all_shelters") if v == "All shelters" else v)
        sex = st.radio(t("disc_sex"), ["Any", "F", "M"], horizontal=True,
                       format_func=lambda v: {"Any": t("disc_any"), "F": t("disc_sex_f"), "M": t("disc_sex_m")}[v])
        breed = st.radio(t("disc_breed"), ["Any", "Mixed-breed", "Purebred"], horizontal=True,
                         format_func=lambda v: {"Any": t("disc_any"), "Mixed-breed": t("disc_mixed"), "Purebred": t("disc_purebred")}[v])
        age = st.radio(t("disc_age"), ["Any", "CHILD", "ADULT"], horizontal=True,
                       format_func=lambda v: {"Any": t("disc_any"), "CHILD": t("disc_child"), "ADULT": t("disc_adult")}[v])
        ster = st.radio(t("disc_ster"), ["Any", "Yes", "No", "Unknown"], horizontal=True,
                        format_func=lambda v: {"Any": t("disc_any"), "Yes": t("disc_yes"), "No": t("disc_no"), "Unknown": t("disc_unknown")}[v])
        body = st.selectbox(t("disc_body"), ["Any"] + sorted(df["body_type"].dropna().unique()),
                            format_func=lambda v: t("disc_any") if v == "Any" else v)
        lo, hi = st.slider(t("disc_score_slider"), 0, 100, (0, 100), step=5, help=t("disc_score_help"))
        sort_label = st.selectbox(t("disc_sort_by"), list(SORTS.keys()), format_func=lambda k: t(_SORT_KEYS[k]))
        n_show = st.slider(t("disc_how_many"), 3, 24, 10, step=1)
        shuffled = st.button(t("disc_shuffle"), use_container_width=True)

    view = _filter(df, shelter, sex, breed, age, ster, body, lo / 100, hi / 100)
    sort = SORTS[sort_label]
    data_sort = sort is not None and sort[0] == "score_data"

    if len(view) == 0:
        st.warning(c["no_match"])
        return

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
    with st.spinner(t("disc_spinner_photos").format(n=len(rows))):
        if sort is not None and sort[0] in ("data_image", "image_only"):
            col, asc = sort

            def _key(row):
                s = _score_dog(str(row["animal_id"]), row["photo_url"],
                               tuple(features.taiwan_row_to_shared6(row).tolist()))
                if not s.get("ok"):
                    return (1, 0.0)
                return (0, s[col][0] if asc else -s[col][0])
            rows.sort(key=_key)
        for row in rows:
            _card(row, n_test)
            st.divider()
