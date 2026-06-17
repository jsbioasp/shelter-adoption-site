<!-- Datasets page copy. Edit the words; each block starts with @name.
     Blocks with {braces} get a live number filled in by the page — keep the braces. -->

@petfinder
### PetFinder (Malaysia)
~8,000 dogs with **photos, descriptions, and resolved adoption outcomes**. Where we *train* the photo model — it has everything a supervised model needs. *What predicts adoption when you can see the listing?*

@austin
### Austin Animal Center (USA)
~40,000 dog records with **resolved outcomes but no photos or descriptions** — demographics only. A *second* training set: pooling it with PetFinder teaches the model demographic patterns that **aren't specific to one country**. *What about adoption generalizes across shelters?*

@taiwan
### Taiwan MOA shelters
Thousands of currently-adoptable dogs from Taiwan's public open-data feed — **live, but no outcome labels**. Where we *deploy and test transfer*. *Does what we learned travel to Taiwan?*

@why_dogs
Dogs are the larger, more balanced population in both datasets, and shelter listings are where a prediction can actually change an outcome. Cats and other species were out of scope to keep the comparison clean.

@challenges_intro
Honest modeling starts with knowing what's *wrong* with your data. Each of the three has a different fundamental limitation — and those limitations shape every result below.

@challenge_petfinder
**PetFinder — an arbitrary finish line.**

The label is *adopted within 30 days*. But 30 days is a cutoff someone chose; a dog adopted on day 31 looks identical to one never adopted. The target really splits dogs into "faster vs slower than typical" more than "adopted vs not" — so the ceiling isn't the model, it's the fuzziness of the line itself.

@challenge_taiwan
**Taiwan — no outcomes, and a biased roster.**

The feed is *current stock only*: the moment a dog is adopted it **leaves**. So we literally never see an adopted Taiwan dog — only the ones still waiting, who skew **hard-to-adopt** (older, bigger, fewer photos). With no labels at all, we can only *infer* transfer via the statistical gap with PetFinder. And the fields are coarse: age is just CHILD/ADULT (no senior), color is free-text, often one photo per dog.

@challenge_austin
**Austin — outcomes, but blind.**

Resolved adoption outcomes for tens of thousands of dogs — but **no photos and no descriptions**, just demographics. Perfect for learning what *transfers* across shelters (the shared trunk behind the 0.927), useless for anything a picture would tell you.

@bias_note
**The deployed photo model learned this bias.** Our photo+data model trains its trunk on PetFinder **and** Taiwan photos (domain-invariant), so it reads the *dog* not the photographer's style. But because Taiwan's roster is all hard-to-adopt leftovers, it also inherits a slightly pessimistic world-view — it tends to score Taiwan dogs **lower** than their demographics alone would suggest. The dataset's selection bias is baked right into the model's reads on the Discover Dogs page.

@rankings_success
**Rankings transfer across countries.** Over the {n_shelters} shelters with published government adoption rates, our model's ranking matched the government's at **ρ = {spearman}** (1.0 would be identical order) — the *order* transfers even though the *absolute* rates don't.

@ranking_caption
Government rank is by published adoption rate; the three New Taipei shelters share the same 95% rate (a 3-way tie for #1). Our model puts them in its top 3 and pins the lowest-rate shelters at the bottom — the only disagreement is one adjacent swap, Kaohsiung edging out Taipei City, and that single inversion is the whole gap from a perfect 1.0. {source}

@ranking_scope
Scope: this is the validated set — the 7 shelters with a published government rate. Counted across every shelter that maps to a rated city, the agreement weakens (the model can't tell apart shelters within the same city), so the claim stays scoped to these 7.

@ranking_how
**Spearman rank correlation** asks one question: if you rank Taiwan's shelters by the model's *average predicted adoption*, do they come out in the **same order** as their real published rates? **+1** = identical order, **0** = unrelated, **−1** = exactly backwards. The model never sees a single Taiwan outcome — it only ranks.

**The 0.927 comes from the cross-dataset model — and this is where Austin earns its place.** Train *one* model with a **shared trunk** and a **separate head per dataset** on PetFinder **and** Austin together, and the shared trunk is forced to learn demographic patterns common to *both* countries. That cross-trained model ranks Taiwan's shelters at **0.927** — versus **0.778** for a model trained on PetFinder alone. The second dataset is what makes the ranking travel.

Note: this ranking uses **tabular features only** — photos are deliberately left *out* of the Taiwan ranking, because (see the failures below) photo style doesn't cross borders. Demographics do.

@photos_win
**Photos add real signal.** Adding CNN photo features lifts adoption AUC by **{lift}** over the tabular baseline. *From our experiments.*

@one_lever
**One lever beats a fancy model.** Within young mixed-breed dogs, caged photos are associated with **{caged}** in 30-day adoption. *From our experiments.*

@photo_count
**A few photos beat none — or too many.** Adoption is non-monotonic in photo count: it peaks at **4–6 photos (~49%)**, versus **~30%** for *no* photo and **~38%** for *16+*. A small, focused set wins; piling on a dozen photos drops back toward the no-photo range. *(Verified on the 8,132-dog PetFinder set; PhotoAmt is a listing lever, not a deployed-model feature.)*

@photo_transfer
**Photo features don't transfer cleanly.** The CNN trained on Malaysian listings scored Taipei City's institutional photos *lowest* — even though Taipei has Taiwan's highest published adoption rate. Photo content is location-specific.

@photo_transfer_deep
**The deeper story — and a lesson in when *not* to ship the fancy model.** *Why* do the photos transfer worse? The CNN reads photo **style**, not the dog: it learned "polished marketplace photo → adopts, institutional shelter photo → doesn't" on the Malaysian listings, and Taiwan's shelters are *all* institutional. We tried a fix — train the photo trunk to read the same dog attributes from **both** countries' photos (domain-invariant training). Tested honestly on *new dogs at the known shelters*, it **does** transfer (rank correlation **+0.53**) — a real result, not an artifact. **But it doesn't beat the simple data-only model (+0.59)**, it's noisier, and on *brand-new* shelters it inverts. So for the **cross-shelter ranking** (which shelters need support most), this site uses the **data-only** model — the photo fix only *matches* it there, and the simpler, steadier model wins. *(The domain-invariant model **is** deployed for **per-dog** photo reads, where its sharper image handling earns its keep — see Try the Models.)* Match the tool to the job. *M06-MULTITASK-FINDINGS.md, domain-invariant trunk addendum (held-out tests).*

@tabular_ceiling
**Tabular data hits a ceiling fast.** Demographics alone cap out around **{ceiling}**. No amount of model tuning broke past it — the information just isn't in the columns.

@taiwan_not_loaded
Taiwan snapshot not loaded yet — the Discover Dogs page explains the scheduled refresh.
