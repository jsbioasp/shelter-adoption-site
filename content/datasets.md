<!-- Datasets page copy. Edit the words; each block starts with @name.
     Blocks with {braces} get a live number filled in by the page — keep the braces. -->

@petfinder
### PetFinder (Malaysia)
~8,000 dogs with **photos, descriptions, and resolved adoption outcomes**. This is where we *train* — it has everything a supervised model needs. It answers: *what predicts adoption when you can see the listing?*

@taiwan
### Taiwan MOA shelters
Thousands of currently-adoptable dogs from Taiwan's public open-data feed — **live, but no outcome labels**. This is where we *deploy and test transfer*. It answers: *does what we learned in Malaysia travel to Taiwan?*

@why_dogs
Dogs are the larger, more balanced population in both datasets, and shelter listings are where a prediction can actually change an outcome. Cats and other species were out of scope to keep the comparison clean.

@rankings_success
**Rankings transfer across countries.** Over the {n_shelters} shelters with published government adoption rates, our model's ranking matched the government's at **ρ = {spearman}** (1.0 would be identical order) — the *order* transfers even though the *absolute* rates don't.

@ranking_caption
Government rank is by published adoption rate; the three New Taipei shelters share the same 95% rate (a 3-way tie for #1). Our model puts them in its top 3 and pins the lowest-rate shelters at the bottom — the only disagreement is one adjacent swap, Kaohsiung edging out Taipei City, and that single inversion is the whole gap from a perfect 1.0. {source}

@ranking_scope
Scope: this is the validated set — the 7 shelters with a published government rate. Counted across every shelter that maps to a rated city, the agreement weakens (the model can't tell apart shelters within the same city), so the claim stays scoped to these 7.

@photos_win
**Photos add real signal.** Adding CNN photo features lifts adoption AUC by **{lift}** over the tabular baseline. *From our experiments.*

@one_lever
**One lever beats a fancy model.** Within young mixed-breed dogs, caged photos are associated with **{caged}** in 30-day adoption. *From our experiments.*

@photo_transfer
**Photo features don't transfer cleanly.** The CNN trained on Malaysian listings scored Taipei City's institutional photos *lowest* — even though Taipei has Taiwan's highest published adoption rate. Photo content is location-specific.

@tabular_ceiling
**Tabular data hits a ceiling fast.** Demographics alone cap out around **{ceiling}**. No amount of model tuning broke past it — the information just isn't in the columns.

@taiwan_not_loaded
Taiwan snapshot not loaded yet — the Discover Dogs page explains the scheduled refresh.
