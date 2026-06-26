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
}


def t(key: str) -> str:
    """Current-language UI string for `key`; English fallback, then the key itself."""
    try:
        lang = st.session_state.get("lang", "en")
    except Exception:
        lang = "en"
    entry = UI.get(key, {})
    return entry.get(lang) or entry.get("en") or key
