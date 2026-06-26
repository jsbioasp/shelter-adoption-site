"""Plain-English / 白話 definitions of the terms the site uses, in one place.

render(st, *keys) shows, inline at the top of a page, just the terms that page
actually uses, so each page explains its own jargon and no term drifts between
pages. Each term carries both languages; the renderer picks the current one from
st.session_state["lang"], English as the fallback.
"""
from __future__ import annotations

TERMS: dict[str, dict[str, str]] = {
    "auc": {
        "en": "**AUC** — how well the model ranks a random adopted dog above a random "
              "not-yet-adopted one. 0.5 is a coin flip, 1.0 is perfect; our ~0.70 is fair, not great.",
        "zh": "**AUC**——衡量模型把一隻隨機被領養的狗，排在一隻隨機尚未被領養的狗之前的能力有多好。"
              "0.5 等於擲銅板，1.0 是完美；我們的 ~0.70 算尚可，但不算優秀。",
    },
    "rank_agreement": {
        "en": "**Rank agreement (Spearman)** — whether two rankings put things in the same order. "
              "1.0 = identical order, 0 = unrelated. We use it to compare our shelter ranking "
              "against the government's published adoption rates.",
        "zh": "**等級一致性（Spearman）**——衡量兩份排名是否把東西排成相同順序。1.0 = 完全相同，"
              "0 = 毫無關聯。我們用它來比較我們的收容所排名與政府公布的領養率。",
    },
    "calibration": {
        "en": "**Calibration** — whether a score means what it says: if the model says 70%, do "
              "about 70% of those dogs actually get adopted? A calibrated score can be read as a "
              "real probability.",
        "zh": "**校準（Calibration）**——衡量分數是否名實相符：如果模型說 70%，那群狗是否真的約有 "
              "70% 被領養？校準良好的分數可以當作真正的機率來讀。",
    },
    "ece": {
        "en": "**ECE (expected calibration error)** — how far a score's confidence sits from "
              "reality, on average. If the model says 70% but those dogs adopt 65% of the time, ECE "
              "sums up that 5-point gap. Lower is better; ~0.05 means predictions land within about "
              "5 points.",
        "zh": "**ECE（期望校準誤差）**——衡量模型的信心與現實平均差多遠。如果模型說 70%，但那群狗實際"
              "只有 65% 被領養，ECE 就會把這 5 個百分點的落差加總。越低越好；~0.05 代表預測大約落在"
              "實際值的 5 個百分點以內。",
    },
    "mlp": {
        "en": "**MLP (multi-layer perceptron)** — a small neural network. Ours reads a dog's "
              "demographic facts (age, sex, breed, sterilization) and outputs an adoption-pace score.",
        "zh": "**MLP（多層感知器）**——一種小型神經網路。我們的 MLP 讀取一隻狗的基本資料"
              "（年齡、性別、品種、是否絕育），輸出一個領養速度分數。",
    },
    "cnn": {
        "en": "**CNN (convolutional neural network)** — a network that reads images. Ours turns a "
              "listing photo into numbers, picking up cues like how young the dog looks.",
        "zh": "**CNN（卷積神經網路）**——一種讀取影像的網路。我們的 CNN 把刊登照片轉換成數字，"
              "抓出像是「這隻狗看起來多年輕」之類的線索。",
    },
    "multitask": {
        "en": "**Multi-task** — training one network to predict two things at once so it learns "
              "better. Our photo model predicts adoption *and* 'is this a puppy?', which sharpens "
              "what it reads from the picture. (A separate, demographics-only model does the "
              "cross-country shelter ranking — photo style doesn't travel between countries, so "
              "photos are left out of that one.)",
        "zh": "**多任務（Multi-task）**——訓練一個網路同時預測兩件事，讓它學得更好。我們的照片模型"
              "同時預測「會不會被領養」*以及*「這是幼犬嗎？」，藉此讓它從照片中讀到的資訊更銳利。"
              "（另有一個只用基本資料的模型負責跨國的收容所排名——因為照片風格無法跨國通用，"
              "所以那個模型不使用照片。）",
    },
    "strata": {
        "en": "**Strata** — the four demographic groups we compare within: young vs adult × "
              "purebred vs mixed-breed. Measuring an effect inside one group keeps the comparison "
              "like-for-like.",
        "zh": "**分層（Strata）**——我們用來互相比較的四個族群：幼年對成年 × 純種對米克斯。"
              "在同一族群內測量效果，能讓比較維持在「同類對同類」。",
    },
    "pp": {
        "en": "**pp (percentage points)** — the plain gap between two percentages. From a 30% "
              "adoption rate to 47% is a rise of 17 points (17pp); we say 'points' so it isn't "
              "confused with a 'percent increase'.",
        "zh": "**pp（百分點）**——兩個百分比之間單純的差距。從 30% 的領養率到 47%，是上升了 17 個"
              "百分點（17pp）；我們說「點」是為了避免和「百分比的增幅」搞混。",
    },
}

_LABEL = {"en": "Plain-English glossary", "zh": "白話詞彙表"}


def render(st, *keys, label=None):
    """Drop an inline glossary of the requested terms in the current language."""
    try:
        lang = st.session_state.get("lang", "en")
    except Exception:
        lang = "en"
    if lang not in ("en", "zh"):
        lang = "en"
    lbl = label if label is not None else _LABEL[lang]
    lines = []
    for k in keys:
        term = TERMS.get(k)
        if term:
            lines.append("- " + (term.get(lang) or term["en"]))
    if lines:
        st.markdown(f"**{lbl}**\n\n" + "\n".join(lines))
