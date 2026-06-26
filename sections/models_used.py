"""Models Used section — what the three model types are and what they do.

Owner: <student>. Words live in content/models_used.md; the two diagrams are
plain Graphviz DOT strings rendered with st.graphviz_chart (no extra dependency
— Streamlit draws the DOT in the browser).
"""
import streamlit as st

from lib import content


def _mlp_dot() -> str:
    """Conceptual MLP: the 6 demographic features -> a hidden layer -> one score."""
    inputs = ["age ≥ 1y", "age < 6m", "mixed-breed", "male", "female", "spayed/neutered"]
    out = [
        "digraph {",
        'rankdir=LR; bgcolor="transparent"; nodesep=0.18; ranksep="1.0";',
        'node [fontname="sans-serif", fontsize=10, color="#9e9e9e"];',
        'edge [color="#d8d8d8", arrowsize=0.4];',
        'subgraph cluster_in { label="Inputs — 6 features"; style=dashed; color="#cccccc";',
    ]
    for i, lbl in enumerate(inputs):
        out.append(f'  i{i} [label="{lbl}", shape=box, style="rounded,filled", fillcolor="#E1F5FE"];')
    out.append("}")
    out.append('subgraph cluster_h { label="Hidden layer"; style=dashed; color="#cccccc";')
    for h in range(6):
        out.append(f'  h{h} [label="", shape=circle, style=filled, fillcolor="#E8F5E9", width=0.35, fixedsize=true];')
    out.append("}")
    out.append('subgraph cluster_out { label="Output"; style=dashed; color="#cccccc";')
    out.append('  y [label="P(adopt)", shape=box, style="rounded,filled", fillcolor="#FFE0B2"];')
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
        'photo [label="Dog photo\\n(pixels)", fillcolor="#E1F5FE"];',
        'c1 [label="Conv stage 1\\nedges, textures", fillcolor="#E8F5E9"];',
        'c2 [label="Conv stage 2\\near, snout, fur", fillcolor="#E8F5E9"];',
        'c3 [label="Conv stage 3\\nwhole-dog features", fillcolor="#E8F5E9"];',
        'feat [label="Feature vector\\n(numbers)", fillcolor="#F3E5F5"];',
        'y [label="adoption score", fillcolor="#FFE0B2"];',
        "photo -> c1 -> c2 -> c3 -> feat -> y;",
        "}",
    ])


def render():
    c = content.load("models_used")
    st.title("Models Used")
    st.markdown(c["intro"])

    st.markdown(c["mlp"])
    st.graphviz_chart(_mlp_dot())
    st.caption("Simplified: six demographic features feed a hidden layer that outputs one "
               "adoption score. (Illustrative — the real network has more hidden units.)")

    st.markdown(c["cnn"])
    st.graphviz_chart(_cnn_dot())
    st.caption("Simplified photo path: the image passes through stages that build from simple "
               "edges to whole-dog features, then a single feature vector. (ConvNeXt-Tiny has "
               "many more layers.)")

    st.markdown(c["multitask"])
