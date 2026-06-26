<!-- Datasets page copy. Edit the words; each block starts with @name.
     Blocks with {braces} get a live number filled in by the page — keep the braces. -->

@petfinder
### PetFinder (Malaysia)
~8,000 dogs with **photos, descriptions, and resolved adoption outcomes**. Where we *train* the photo model — it has everything a supervised model needs. *What predicts adoption when you can see the listing?*

Source: [PetFinder.my Adoption Prediction on Kaggle](https://www.kaggle.com/competitions/petfinder-adoption-prediction)

@austin
### Austin Animal Center (USA)
~40,000 dog records with **resolved outcomes but no photos or descriptions** — demographics only. A *second* training set: pooling it with PetFinder teaches the model demographic patterns that **aren't specific to one country**. *What about adoption generalizes across shelters?*

Source: [Austin Animal Center Outcomes — City of Austin open data](https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes-10-01-2013-to-05-05-/9t4d-g238)

@taiwan
### Taiwan MOA shelters
Thousands of currently-adoptable dogs from Taiwan's public open-data feed — **live, but no outcome labels**. Where we *deploy and test transfer*. *Does what we learned travel to Taiwan?*

Source: [Taiwan Ministry of Agriculture open data](https://data.gov.tw/en/datasets/85903)

@challenges_intro
Each of the three is suited to a different job, and each has real flaws — a different one in each case. Knowing those strengths and limits is what keeps the results below honest.

@challenge_petfinder
**PetFinder — the 30-day cutoff is arbitrary.**

The label is *adopted within 30 days*. Thirty days is a line someone picked — a dog adopted on day 31 counts the same as one never adopted — but it happens to fall near the average: roughly 50% of the dataset lands on either side of the threshold. So "within 30 days" really means *faster vs slower than a typical dog*, not *adopted vs not* — and the ceiling on accuracy is the fuzziness of that line, not the model.

@challenge_taiwan
**Taiwan — no outcomes, and an active roster.**

Adopted dogs are removed from the dataset the moment they're placed, so we never see a Taiwan adoption — only the dogs still listed, who skew harder to adopt (older, bigger, fewer photos). We have no way of knowing the actual adoption trends except by inferring them from PetFinder. The fields are coarse, too: age is just CHILD or ADULT, with no stated line between them; color is free text; and there's often a single photo per dog.

@challenge_austin
**Austin — outcomes, but no photos or text.**

Tens of thousands of resolved outcomes, but only demographics — no photos, no descriptions. That makes it good for learning what holds up across shelters (the cross-dataset model behind the 0.927), and no help for anything a picture would tell you.

@bias_note
**The deployed photo model picked up this skew.** Our photo model is trained on **both** PetFinder and Taiwan photos, so it reads the *dog*, not the photographer's style. But because the Taiwan dogs it learned from are all ones still waiting (harder to adopt), it leans low on Taiwan — it tends to score Taiwan dogs **lower** than their demographics alone would suggest. That selection bias shows up directly in the model's reads on the Discover Dogs page.

@rankings_success
**Rankings transfer across countries.** Over the {n_shelters} shelters with published government adoption rates, our model's ranking matched the government's at **ρ = {spearman}** (1.0 would be identical order) — the *order* transfers even though the *absolute* rates don't.

@ranking_caption
Government rank is by published adoption rate; the three New Taipei shelters share the same 95% rate (a 3-way tie for #1). Our model puts them in its top 3 and pins the lowest-rate shelters at the bottom — the only disagreement is one adjacent swap, Kaohsiung edging out Taipei City, and that single inversion is the whole gap from a perfect 1.0. {source}

@ranking_scope
Scope: this is the validated set — the 7 shelters with a published government rate, and the larger ones where the rate is stable. Across every shelter that maps to a rated city the agreement weakens, for two reasons: the model can't tell apart shelters within the same city, and smaller shelters handle so few dogs that their adoption rate swings widely on chance alone. So the claim stays scoped to these 7, where the numbers are big enough to be reliable.

@ranking_how
**Spearman rank correlation** asks one question: if you rank Taiwan's shelters by the model's *average predicted adoption*, do they come out in the **same order** as their real published rates? **+1** = identical order, **0** = unrelated, **−1** = exactly backwards. The model never sees a single Taiwan outcome — it only ranks.

**The 0.927 comes from the cross-dataset model — and this is where Austin earns its place.** Train *one* model with a **shared trunk** and a **separate head per dataset** on PetFinder **and** Austin together, and the shared trunk is forced to learn demographic patterns common to *both* countries. That cross-trained model ranks Taiwan's shelters at **0.927** — versus **0.778** for a model trained on PetFinder alone. The second dataset is what makes the ranking travel.

Note: this ranking uses **tabular features only** — photos are deliberately left *out* of the Taiwan ranking, because photo style doesn't cross borders. Demographics do.

@taiwan_not_loaded
Taiwan snapshot not loaded yet — the Discover Dogs page explains the scheduled refresh.
