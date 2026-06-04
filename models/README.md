# Models

- `m06_ensemble.pkl` (1 MB) — 5-seed multi-task ensemble. Dict with
  `state_dicts`, `img_scaler`, `tab_scaler`, `aucs`, `n_img=768`, `n_tab=6`.
  Loaded by `lib/models.MultiTaskMLP`. Photo + data scoring.
- `m06_tabular_only.pkl` (59 KB) — 5-seed FlatMLP ensemble on SHARED_6.
  Loaded by `lib/models.FlatMLP`. Data-only scoring.

Both come from the M06 experiments. The architectures are vendored in
`lib/models.py`; the state-dict keys must match those classes exactly.
