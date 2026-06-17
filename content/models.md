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
