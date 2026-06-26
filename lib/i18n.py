"""UI-string translations — the chrome that isn't page prose.

Page prose lives in content/<lang>/*.md. The strings hardcoded in sections/*.py
(section headers, widget labels, captions, table columns, diagram labels) live
here so they translate too. t("key") returns the current language's string, with
English as the fallback for anything not yet translated, then the key itself.

Add an entry as {"en": "...", "zh": "..."}; the section calls t("key").
"""
from __future__ import annotations

import streamlit as st

UI: dict[str, dict[str, str]] = {
    # ---- app + navigation ----
    "site_title": {"en": "Shelter Adoption ML", "zh": "收容所領養預測"},
    "nav_motivation": {"en": "Introduction and Motivations", "zh": "簡介與動機"},
    "nav_datasets": {"en": "Datasets & Experiments", "zh": "資料集與實驗"},
    "nav_models_used": {"en": "Models Used", "zh": "使用的模型"},
    "nav_results": {"en": "Results", "zh": "結果"},
    "nav_models_ui": {"en": "Try the Models", "zh": "試用模型"},
    "nav_discover": {"en": "Discover Dogs", "zh": "尋找狗狗"},
    "nav_next_steps": {"en": "Next Steps", "zh": "下一步"},
    "nav_disclaimer": {"en": "Disclaimer", "zh": "免責聲明"},

    # ---- Introduction and Motivations ----
    "h_research_background": {"en": "Research background and motivation", "zh": "研究背景與動機"},
    "h_research_objectives": {"en": "Research objectives", "zh": "研究目標"},
    "h_methodology": {"en": "Methodology and implementation", "zh": "研究方法與實作"},
    "h_expected_contributions": {"en": "Expected contributions", "zh": "預期貢獻"},
    "h_what_you_can_do": {"en": "What you can do here", "zh": "你可以在這裡做什麼"},
    "h_authors": {"en": "Authors", "zh": "作者"},

    # ---- Models Used (captions + diagram labels) ----
    "mu_cap_mlp": {"en": "Simplified: six demographic features feed a hidden layer that outputs one adoption score. (Illustrative — the real network has more hidden units.)",
                   "zh": "簡化版：六個基本特徵輸入一個隱藏層，輸出一個領養分數。（示意圖——實際的網路有更多隱藏單元。）"},
    "mu_cap_cnn": {"en": "Simplified photo path: the image passes through stages that build from simple edges to whole-dog features, then a single feature vector. (ConvNeXt-Tiny has many more layers.)",
                   "zh": "簡化的照片流程：影像經過數個階段，從簡單的邊緣逐步建立到整隻狗的特徵，最後變成一個特徵向量。（ConvNeXt-Tiny 的層數遠多於此。）"},
    "mu_cap_mt": {"en": "The photo and demographics share one backbone, which then splits into two heads — one for adoption, one for age. Practicing the age question sharpens the features the adoption head reads.",
                  "zh": "照片與基本資料共用一個主幹，再分成兩個輸出頭——一個負責領養，一個負責年齡。練習判斷年齡，會讓領養輸出頭所讀取的特徵更銳利。"},
    "dg_inputs": {"en": "Inputs — 6 features", "zh": "輸入——6 個特徵"},
    "dg_hidden": {"en": "Hidden layer", "zh": "隱藏層"},
    "dg_output": {"en": "Output", "zh": "輸出"},
    "dg_age_adult": {"en": "age ≥ 1y", "zh": "年齡 ≥ 1 歲"},
    "dg_age_young": {"en": "age < 6m", "zh": "年齡 < 6 個月"},
    "dg_mixed": {"en": "mixed-breed", "zh": "米克斯"},
    "dg_male": {"en": "male", "zh": "公"},
    "dg_female": {"en": "female", "zh": "母"},
    "dg_fixed": {"en": "spayed/neutered", "zh": "已絕育"},
    "dg_p_adopt": {"en": "P(adopt)", "zh": "領養機率"},
    "dg_photo": {"en": "Dog photo\\n(pixels)", "zh": "狗狗照片\\n（像素）"},
    "dg_conv1": {"en": "Conv stage 1\\nedges, textures", "zh": "卷積階段 1\\n邊緣、紋理"},
    "dg_conv2": {"en": "Conv stage 2\\near, snout, fur", "zh": "卷積階段 2\\n耳朵、口鼻、毛"},
    "dg_conv3": {"en": "Conv stage 3\\nwhole-dog features", "zh": "卷積階段 3\\n整隻狗的特徵"},
    "dg_featvec": {"en": "Feature vector\\n(numbers)", "zh": "特徵向量\\n（數字）"},
    "dg_adopt_score": {"en": "adoption score", "zh": "領養分數"},
    "dg_photo2": {"en": "Dog photo", "zh": "狗狗照片"},
    "dg_data": {"en": "6 demographic\\nfeatures", "zh": "6 個基本\\n特徵"},
    "dg_backbone": {"en": "Shared backbone", "zh": "共用主幹"},
    "dg_adopt_head": {"en": "Adoption head", "zh": "領養輸出頭"},
    "dg_age_head": {"en": "Age head", "zh": "年齡輸出頭"},
    "dg_q_adopt": {"en": "Will it be adopted?\\n(main goal)", "zh": "會被領養嗎？\\n（主要目標）"},
    "dg_q_age": {"en": "Is it young?\\n(side goal)", "zh": "是幼犬嗎？\\n（次要目標）"},

    # ---- Datasets & Experiments ----
    "ds_h_three_datasets": {"en": "Three datasets, three jobs", "zh": "三個資料集，三種任務"},
    "ds_h_purposes": {"en": "What the datasets' purposes are, and their strengths and weaknesses",
                      "zh": "這些資料集的用途，以及它們的優勢與弱點"},
    "ds_h_rankings": {"en": "Rankings transfer across countries", "zh": "排名能跨國遷移"},
    "ds_h_how_measure": {"en": "How we measure transfer — and which model earns the 0.927",
                         "zh": "我們如何衡量遷移——以及是哪個模型達成 0.927"},
    "ds_h_live_data": {"en": "The live Taiwan data, right now", "zh": "此刻的台灣即時資料"},
    "ds_m_adoptable": {"en": "Adoptable dogs", "zh": "可領養的狗"},
    "ds_m_shelters": {"en": "Shelters", "zh": "收容所數"},
    "ds_m_mixed_share": {"en": "Mixed-breed share", "zh": "米克斯比例"},
    "ds_by_shelter": {"en": "Adoptable dogs by shelter (top 12)", "zh": "各收容所可領養的狗（前 12 名）"},
    "ds_ranking_source": {"en": "Reproduced from our cross-dataset experiments (per-shelter mean over 3 seeds).",
                          "zh": "由我們的跨資料集實驗重現（每間收容所取 3 個隨機種子的平均）。"},
    "col_our_rank": {"en": "Our rank", "zh": "我們的排名"},
    "col_shelter": {"en": "Shelter", "zh": "收容所"},
    "col_published": {"en": "Published", "zh": "公布領養率"},
    "col_our_score": {"en": "Our score", "zh": "我們的分數"},
    "col_gov_rank": {"en": "Gov rank", "zh": "政府排名"},
    "col_shift": {"en": "Shift", "zh": "變動"},
}


def t(key: str) -> str:
    """Current-language UI string for `key`; English fallback, then the key itself."""
    try:
        lang = st.session_state.get("lang", "en")
    except Exception:
        lang = "en"
    entry = UI.get(key, {})
    return entry.get(lang) or entry.get("en") or key
