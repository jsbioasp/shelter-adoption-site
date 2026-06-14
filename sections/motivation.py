"""Landing / Motivation section. Owner: <student>.

Why this project exists. Keep it concrete and honest — what the tool does and
doesn't do for shelters.
"""
import streamlit as st


def render():
    st.title("🐕 Shelter Adoption ML")
    st.markdown(
        "**A working tool — and an honest account of what machine learning can and "
        "can't do — for animal shelters.**"
    )

    st.markdown("## Why this matters")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            "### Help shelters\n"
            "Shelters triage hundreds of animals with limited staff. A model that "
            "flags which dogs are likely to wait longest lets staff put effort where "
            "it changes an outcome — a better photo, an earlier foster, a featured "
            "listing."
        )
    with col2:
        st.markdown(
            "### Efficiency & effectiveness\n"
            "The same prediction that ranks a dog also explains *why*. The clearest "
            "lever we found isn't a fancy model — it's an uncaged listing photo, which "
            "helps the large group of young, mixed-breed dogs the most. (Young purebred "
            "puppies already adopt fastest.) Small changes, measurable lift."
        )
    with col3:
        st.markdown(
            "### Social impact\n"
            "Faster adoptions mean shorter shelter stays, less crowding, fewer "
            "euthanizations. The goal is a tool a real shelter could use this week — "
            "not a leaderboard score."
        )

    st.markdown("## What you can do here")
    st.markdown(
        "- **Try the models** — score your own dog's data, photo, or both, and see "
        "the predicted adoption pace with an honest confidence read.\n"
        "- **Discover dogs** — browse live, currently-adoptable dogs from Taiwan's "
        "public shelter feed, searchable by shelter.\n"
        "- **See the results** — the best models, what they get right, and where they "
        "break down.\n"
        "- **Read the experiments** — why PetFinder and Taiwan, and the successes and "
        "failures behind the numbers."
    )

    st.info(
        "**Honest framing:** these models are decision *support*, not decision makers. "
        "The clearest lever is a simple one (an uncaged listing photo, within a "
        "demographic group), the model's accuracy is modest (AUC ≈ 0.70), and every "
        "prediction is observational, not causal. The Results page is candid about the limits."
    )
