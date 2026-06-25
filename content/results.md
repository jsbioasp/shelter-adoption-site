<!-- Results page copy. Edit the words; each block starts with @name.
     Blocks with {braces} get a live, measured number filled in by the page — keep the braces.
     The tables and the model tooltips are built in sections/results.py. -->

@score_meaning
**What every score on this site means.** We trained on whether a dog was adopted within 30 days — which split our PetFinder data almost exactly in half (~50%), so 30 days is roughly the *typical* adoption time. Read every score as **adoption pace vs a typical dog**: 50% = average, higher = likely faster, lower = likely slower.

@auc_caption
AUC = how well the model ranks a random adopted dog above a random non-adopted one. 0.5 is a coin flip; 1.0 is perfect. These are the *actual* 5-seed ensembles serving predictions on this site.

@ladder_caption
The deployed model is a touch below the research ceiling — it trades a little AUC for a small, self-contained set of features that work on any shelter's data — we'd rather be honest than chase a leaderboard score.

@why_photo_model
**Why *this* photo model.** The deployed photo+data model is **domain-invariant**: its ConvNeXt trunk was trained on **both** PetFinder and Taiwan shelter photos, so it learns to read the *dog* rather than the photographer's style. That makes it the **sharper ranker** (AUC ~0.72) with more sensible per-photo reads — which is why we deploy it. The trade is a little **calibration**: its probabilities run slightly looser (ECE ~0.05 vs ~0.02 for a PetFinder-only model — predicted ≈ actual within ~5 points instead of ~2). We judged the better image handling worth the looser probabilities.

@confident_about
- **Confident & right:** young dogs in uncaged listing photos — the model and the outcomes agree. (Young *purebred* puppies adopt fastest of all; the caged-photo lever helps the much larger young, mixed-breed group most.)
- **Confident & wrong:** cross-shelter transfer. The photo model is confident on Taiwan institutional photos and confidently wrong — see the Datasets page.
- **Honest uncertainty:** for adult purebreds the signal is thin; the model says so with probabilities near the base rate.

@photo_preliminary
Photo findings are preliminary. An uncaged listing photo is the clearest lever; other composition factors (framing, pose, focus) show smaller, less consistent effects. We're re-running the image experiments with newer findings and may revise these.

@calibration_intro
A score is only useful if it means what it says. **Calibration** asks: of the dogs the photo+data model rated ~50%, did ~50% actually get adopted? Measured on {n_test:,} held-out dogs, predicted tracks actual across the range — within a few points per bin (the deployed domain-invariant model runs a touch looser than a PetFinder-only one; see *Why this photo model*).

@calibration_caption
Expected Calibration Error (ECE) = **{ece:.3f}** — the average gap between predicted and actual is about **5 points** (the domain-invariant photo model trades a little calibration for sharper ranking — see *Why this photo model*). The photo-only view is looser still (ECE {image_ece:.3f}), which is why the site treats it as a diagnostic, not a probability.

@thresholds_intro
Because the photo+data model is calibrated, you can **act only on dogs it's sure about**: predict above a threshold T (likely adopted) or below 1−T (likely not). Higher T covers fewer dogs but is more accurate on the ones you keep.

@thresholds_caption
This is the confidence lever a shelter actually uses: triage aggressively on the high-confidence dogs, give the uncertain ones a human look.

@why_multitask
**Why a *multi-task* model?** In the experiments, a naive flat concatenation of photo + tabular features was badly overconfident (ECE ≈ 0.20 — it claimed 90% on dogs that adopted ~70% of the time). The multi-task model this site deploys keeps the photo signal in a separate trunk and stays calibrated (ECE ≈ {ece:.2f}). Calibration, not just AUC, is why we chose it.

@photos_win
**Photos add real signal.** Adding CNN photo features lifts adoption AUC by **{lift}** over the tabular baseline. *From our experiments.*

@one_lever
**One lever beats a fancy model.** Within young mixed-breed dogs, caged photos are associated with **{caged}** in 30-day adoption. *From our experiments.*

@photo_count
**A few good photos beat none — or too many.** Adoption isn't linear in photo count: it climbs to a peak around **4–6 photos**, then slips back for 7–10 and 11+. Zero-photo listings do worst of all. A small, focused set wins; piling on a dozen doesn't. *(A PetFinder listing pattern, not a deployed-model feature.)*

@tabular_ceiling
**Tabular data hits a ceiling fast.** Demographics alone cap out around **{ceiling}**. No amount of model tuning broke past it — the information just isn't in the columns.

@photo_transfer
**Photo features don't transfer cleanly.** The CNN trained on Malaysian listings scored Taipei City's institutional photos *lowest* — even though Taipei has Taiwan's highest published adoption rate. Photo content is location-specific.

@photo_transfer_deep
**The deeper story — and a lesson in when *not* to ship the fancy model.** *Why* do the photos transfer worse? The CNN reads photo **style**, not the dog: it learned "polished marketplace photo → adopts, institutional shelter photo → doesn't" on the Malaysian listings, and Taiwan's shelters are *all* institutional. We tried a fix — train the photo trunk to read the same dog attributes from **both** countries' photos (domain-invariant training). Tested honestly on *new dogs at the known shelters*, it **does** transfer (rank correlation **+0.53**) — a real result, not an artifact. **But it doesn't beat the simple data-only model (+0.59)**, it's noisier, and on *brand-new* shelters it inverts. So for the **cross-shelter ranking** (which shelters need support most), this site uses the **data-only** model — the photo fix only *matches* it there, and the simpler, steadier model wins. *(The domain-invariant model **is** deployed for **per-dog** photo reads, where its sharper image handling earns its keep — see Try the Models.)* *M06-MULTITASK-FINDINGS.md, domain-invariant trunk addendum (held-out tests).*
