<!-- Results page copy. Edit the words; each block starts with @name.
     Blocks with {braces} get a live, measured number filled in by the page — keep the braces.
     The tables and the model tooltips are built in sections/results.py. -->

@score_meaning
**What every score on this site means.** We trained on whether a dog was adopted within 30 days — which split our PetFinder data almost exactly in half (~50%), so 30 days is roughly the *typical* adoption time. Read every score as **adoption pace vs a typical dog**: 50% = average, higher = likely faster, lower = likely slower.

@auc_caption
AUC = how well the model ranks a random adopted dog above a random non-adopted one. 0.5 is a coin flip; 1.0 is perfect. These are the *actual* 5-seed ensembles serving predictions on this site.

@ladder_caption
The deployed model is a touch below the research ceiling — it trades a little AUC for a small, self-contained set of features that work on any shelter's data. Honesty over leaderboard.

@confident_about
- **Confident & right:** young dogs in uncaged listing photos — the model and the outcomes agree. (Young *purebred* puppies adopt fastest of all; the caged-photo lever helps the much larger young, mixed-breed group most.)
- **Confident & wrong:** cross-shelter transfer. The photo model is confident on Taiwan institutional photos and confidently wrong — see the Datasets page.
- **Honest uncertainty:** for adult purebreds the signal is thin; the model says so with probabilities near the base rate.

@photo_preliminary
Photo findings are preliminary. An uncaged listing photo is the clearest lever; other composition factors (framing, pose, focus) show smaller, less consistent effects. We're re-running the image experiments with newer findings and may revise these.

@calibration_intro
A score is only useful if it means what it says. **Calibration** asks: of the dogs the photo+data model rated ~50%, did ~50% actually get adopted? Measured on {n_test:,} held-out dogs, the answer is yes — predicted ≈ actual in every bin.

@calibration_caption
Expected Calibration Error (ECE) = **{ece:.3f}** — the average gap between predicted and actual is under ~2 points. The photo-only view is noticeably less calibrated (ECE {image_ece:.3f}), which is why the site treats it as a diagnostic, not a probability.

@thresholds_intro
Because the photo+data model is calibrated, you can **act only on dogs it's sure about**: predict above a threshold T (likely adopted) or below 1−T (likely not). Higher T covers fewer dogs but is more accurate on the ones you keep.

@thresholds_caption
This is the confidence lever a shelter actually uses: triage aggressively on the high-confidence dogs, give the uncertain ones a human look.

@why_multitask
**Why a *multi-task* model?** In the experiments, a naive flat concatenation of photo + tabular features was badly overconfident (ECE ≈ 0.20 — it claimed 90% on dogs that adopted ~70% of the time). The multi-task model this site deploys keeps the photo signal in a separate trunk and stays calibrated (ECE ≈ {ece:.2f}). Calibration, not just AUC, is why we chose it.
