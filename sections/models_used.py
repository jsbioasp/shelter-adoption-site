"""Models Used section — what the three model types are and what they do.

Owner: <student>. Words live in content/<lang>/models_used.md; the captions and
diagram labels come from lib.i18n. The diagrams are plain Graphviz DOT strings
rendered with st.graphviz_chart (no extra dependency — Streamlit draws the DOT
in the browser).
"""
import streamlit as st

from lib import content
from lib.i18n import t


def _mlp_dot() -> str:
    """Conceptual MLP: the 6 demographic features -> a hidden layer -> one score."""
    inputs = [t("dg_age_adult"), t("dg_age_young"), t("dg_mixed"),
              t("dg_male"), t("dg_female"), t("dg_fixed")]
    out = [
        "digraph {",
        'rankdir=LR; bgcolor="transparent"; nodesep=0.18; ranksep="1.0";',
        'node [fontname="sans-serif", fontsize=10, color="#9e9e9e"];',
        'edge [color="#d8d8d8", arrowsize=0.4];',
        'subgraph cluster_in { label="' + t("dg_inputs") + '"; style=dashed; color="#cccccc";',
    ]
    for i, lbl in enumerate(inputs):
        out.append(f'  i{i} [label="{lbl}", shape=box, style="rounded,filled", fillcolor="#E1F5FE"];')
    out.append("}")
    out.append('subgraph cluster_h { label="' + t("dg_hidden") + '"; style=dashed; color="#cccccc";')
    for h in range(6):
        out.append(f'  h{h} [label="", shape=circle, style=filled, fillcolor="#E8F5E9", width=0.35, fixedsize=true];')
    out.append("}")
    out.append('subgraph cluster_out { label="' + t("dg_output") + '"; style=dashed; color="#cccccc";')
    out.append('  y [label="' + t("dg_p_adopt") + '", shape=box, style="rounded,filled", fillcolor="#FFE0B2"];')
    out.append("}")
    for i in range(len(inputs)):
        for h in range(6):
            out.append(f"  i{i} -> h{h};")
    for h in range(6):
        out.append(f"  h{h} -> y;")
    out.append("}")
    return "\n".join(out)


def _cnn_dot() -> str:
    """Conceptual CNN (ConvNeXt-Tiny): photo -> conv stages -> features -> score."""
    return "\n".join([
        "digraph {",
        'rankdir=LR; bgcolor="transparent"; nodesep=0.3; ranksep="0.6";',
        'node [shape=box, style="rounded,filled", fontname="sans-serif", fontsize=10, color="#9e9e9e"];',
        'edge [color="#bdbdbd", arrowsize=0.7];',
        'photo [label="' + t("dg_photo") + '", fillcolor="#E1F5FE"];',
        'c1 [label="' + t("dg_conv1") + '", fillcolor="#E8F5E9"];',
        'c2 [label="' + t("dg_conv2") + '", fillcolor="#E8F5E9"];',
        'c3 [label="' + t("dg_conv3") + '", fillcolor="#E8F5E9"];',
        'feat [label="' + t("dg_featvec") + '", fillcolor="#F3E5F5"];',
        'y [label="' + t("dg_adopt_score") + '", fillcolor="#FFE0B2"];',
        "photo -> c1 -> c2 -> c3 -> feat -> y;",
        "}",
    ])


def _multitask_dot() -> str:
    """Conceptual multi-task model: a shared backbone splitting into two heads."""
    return "\n".join([
        "digraph {",
        'rankdir=LR; bgcolor="transparent"; nodesep=0.35; ranksep="0.7";',
        'node [shape=box, style="rounded,filled", fontname="sans-serif", fontsize=10, color="#9e9e9e"];',
        'edge [color="#bdbdbd", arrowsize=0.7];',
        'photo [label="' + t("dg_photo2") + '", fillcolor="#E1F5FE"];',
        'data [label="' + t("dg_data") + '", fillcolor="#E1F5FE"];',
        'trunk [label="' + t("dg_backbone") + '", fillcolor="#E8F5E9"];',
        'adopt [label="' + t("dg_adopt_head") + '", fillcolor="#FFF3E0"];',
        'age [label="' + t("dg_age_head") + '", fillcolor="#FFF3E0"];',
        'yadopt [label="' + t("dg_q_adopt") + '", fillcolor="#FFE0B2"];',
        'yage [label="' + t("dg_q_age") + '", fillcolor="#F3E5F5"];',
        "photo -> trunk; data -> trunk;",
        "trunk -> adopt -> yadopt;",
        "trunk -> age -> yage;",
        "}",
    ])


def render():
    c = content.load("models_used")
    st.title(t("nav_models_used"))
    st.markdown(c["intro"])

    st.markdown(c["mlp"])
    st.graphviz_chart(_mlp_dot())
    st.caption(t("mu_cap_mlp"))

    st.markdown(c["cnn"])
    st.graphviz_chart(_cnn_dot())
    st.caption(t("mu_cap_cnn"))

    st.markdown(c["multitask"])
    st.graphviz_chart(_multitask_dot())
    st.caption(t("mu_cap_mt"))
