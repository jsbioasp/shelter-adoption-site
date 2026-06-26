<!-- Results page copy. Edit the words; each block starts with @name.
     Blocks with {braces} get a live, measured number filled in by the page — keep the braces.
     The tables and the model tooltips are built in sections/results.py. -->

@score_meaning
**What every score on this site means.** We trained on whether a dog was adopted within 30 days — which split our PetFinder data almost exactly in half (~50%), so 30 days is roughly the *typical* adoption time. Read every score as **adoption pace vs a typical dog**: 50% = average, higher = likely faster, lower = likely slower.

@auc_caption
AUC = how well the model ranks a random adopted dog above a random non-adopted one. 0.5 is a coin flip; 1.0 is perfect. These are the *actual* 5-seed ensembles serving predictions on this site.

@ladder_caption
The deployed model is a touch below the research ceiling — it trades a little AUC for a small, self-contained set of features that work on any shelter's data — we'd rather be honest than chase a leaderboard score.

@confident_about
- **Confident & right:** young dogs in uncaged listing photos — the model and the outcomes agree. (Young *purebred* puppies adopt fastest of all; the caged-photo lever helps the much larger young, mixed-breed group most.)
- **Confident & wrong:** photo scores don't carry over between shelter systems — the model can be confident on a new country's shelter photos and still be wrong.
- **Honest uncertainty:** for adult purebreds the signal is thin; the model says so with probabilities near the base rate.

@photo_preliminary
Photo findings are preliminary. An uncaged listing photo is the clearest lever; other composition factors (framing, pose, focus) show smaller, less consistent effects. We're re-running the image experiments with newer findings and may revise these.

@calibration_intro
A score is only useful if it means what it says. **Calibration** asks: of the dogs the photo+data model rated ~50%, did ~50% actually get adopted? Measured on {n_test:,} held-out dogs, predicted tracks actual across the range — within a few points per bin.

@calibration_caption
Expected Calibration Error (ECE) = **{ece:.3f}** — the average gap between predicted and actual is about **5 points**. The photo-only view is looser still (ECE {image_ece:.3f}), which is why the site treats it as a diagnostic, not a probability.

@thresholds_intro
Because the photo+data model is calibrated, you can **act only on dogs it's sure about**: predict above a threshold T (likely adopted) or below 1−T (likely not). Higher T covers fewer dogs but is more accurate on the ones you keep.

@thresholds_caption
This is the confidence lever a shelter actually uses: triage aggressively on the high-confidence dogs, give the uncertain ones a human look.

@why_multitask
**Why a *multi-task* model?** The simplest way to combine a photo with the demographic facts — gluing all the numbers together — made the model badly overconfident: it claimed 90% sure on dogs that actually adopted ~70% of the time. The multi-task model we deploy keeps the photo and the facts in their own lanes, so its confidence stays honest (ECE ≈ {ece:.2f}). A score you can trust matters as much as a sharp one — that's why we chose it.

@photos_win
**Photos add real signal.** Adding CNN photo features lifts adoption AUC by **{lift}** over the tabular baseline. *From our experiments.*

@one_lever
**One lever beats a fancy model.** Within young mixed-breed dogs, caged photos are associated with **{caged}** in 30-day adoption. *From our experiments.*

@photo_count
**A few good photos beat none — or too many.** Adoption isn't linear in photo count: it climbs to a peak around **4–6 photos**, then slips back for 7–10 and 11+. Zero-photo listings do worst of all. A small, focused set wins; piling on a dozen doesn't. *(A PetFinder listing pattern, not a deployed-model feature.)*

@tabular_ceiling
**Tabular data hits a ceiling fast.** Demographics alone cap out around **{ceiling}**. No amount of model tuning broke past it — the information just isn't in the columns.

@older_dog_signal
**Older dogs need a different lever.** Puppies sell themselves; for **adult purebreds** the editable photo lever is **framing** — wide, full-body shots beat tight face close-ups (+7.7pp adoption). But most of an adult dog's signal is *intrinsic* — who the dog is, not how it's shot — so for older dogs the tool's job is to **surface** the ones who need help, not restyle them.

@sentiment_null
**What didn't help: the words.** We scored each description's sentiment, expecting upbeat write-ups to predict adoption. They didn't — about **85% of descriptions are positive**, so there's barely any signal to split dogs by, and what little exists, the photos and demographics already carry.

@signal_mechanism
For a photo feature to help, two things have to be true: the network can *read* it from the picture, and it *correlates* with adoption. “Is this a puppy?” passes both — the camera sees it (young dogs look young), and young dogs adopt about **13 points faster**. “Is it mixed-breed?” the camera can also see, but it barely moves adoption (**~2 points**), so it adds little. Sentiment fails the first test — descriptions are essentially invisible to a photo model. That's why stacking on more photo-derived features stops helping: the part that's both readable *and* tied to adoption is mostly just *“how young does this dog look?”* — and piling on more demographic cues just re-reads the same thing.
