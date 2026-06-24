<!-- "Try the Models" page copy. Edit the words; each block starts with @name.
     The form controls, the confidence tiers, and the result captions live in
     sections/models_ui.py (they're tied to the scoring logic). -->

@intro
Run the adoption model on your own dog. Pick a mode — the more you give it, the more the prediction has to work with.

@data_tab
Four facts any shelter already knows — the model turns them into six features. No photo needed.

@data_heads_up
Heads-up: with only 6 demographic flags, this model produces just ~16 distinct scores. For a per-dog read, add a photo.

@image_tab
Upload a listing photo. The model reads the dog from the picture alone (demographics zeroed) — useful for *what does the photo say?*

@image_axis_caption
Photo-axis only: the model is reading age/breed/body cues from the pixels, not aesthetics on their own (see the Results page).

@both_tab
The full model: photo **and** demographics together. This is the configuration the Results page reports at AUC ≈ 0.72.

@reshoot_tab
You can't change a dog — but you *can* change its photo. This shows **real shelter dogs with the same profile** that have **strong listing photos**, so you can see what a good photo of a dog like this looks like.

@reshoot_experimental_note
**Highly experimental.** These are real PetFinder dogs with similar demographics and high-quality photos — not edits of your dog. A better photo lifts our model's score only modestly (~+0.07), and it changes the *presentation*, never the dog. Use it for photo coaching, not as a way to make a dog more adoptable.

@reshoot_your_dog_caption
This is *your* dog's score (photo + demographics). The examples below are **different individuals** with the same profile — compare their *photos*, not their dogs.

@reshoot_takeaway
**What to copy from these photos:** the dog fills the frame, faces the camera, is well-lit, and sits against a clean, uncluttered background. Those four composition traits are what our higher-scoring listings share — and they're free to fix on a re-shoot.

@reshoot_honesty_caption
The pace score is *model output*, validated against PetFinder adoption speed (not Taiwan). Photo quality ≠ adoptability: well-photographed dogs don't all adopt fast. Use to coach listings, not to rank animals.
