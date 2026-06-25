<!-- Discover Dogs page copy. Edit the words; each block starts with @name.
     The per-dog card and dialog text is data-driven and lives in
     sections/discover.py. Blocks with {braces} get live counts filled in. -->

@results_intro
**{n_view:,} dogs match your filters** (data score {lo}–{hi}%). Showing {n_shown}. Score = adoption pace vs a typical dog (50% = average; higher = likely faster). These Taiwan dogs have no recorded outcome, so it's a pace estimate by similarity to the PetFinder dogs the model learned from. **Data score** is the demographics-only baseline — it's searchable across every dog, and barely changes between similar dogs, which is exactly why the photo carries the per-dog signal. Photo scores are computed for the dogs shown here, so photo-based sorts order this set.

@model_honesty
Observational, not causal. Use to triage, not to decide.

@no_snapshot
No Taiwan snapshot found. Run `python scripts/fetch_taiwan_dogs.py` to seed `data/taiwan_dogs.csv`.

@no_match
No dogs match these filters. Loosen them (e.g. widen the data-score range).

@contact_caption
The Taiwan open-data feed lists shelters by phone and address only — no email. Use the link above to reach a shelter's website or contact form.
