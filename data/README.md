# Data

- `taiwan_dogs.csv` — normalized snapshot of currently-adoptable dogs from the
  Taiwan MOA open-data feed. Refreshed daily by
  `.github/workflows/fetch_taiwan_dogs.yml`. Columns are defined in
  `lib/data.TAIWAN_COLUMNS`.
- `taiwan_meta.json` — `{fetched_at, n_dogs, n_shelters, source}` for the snapshot.

Do not hand-edit; regenerate with `python scripts/fetch_taiwan_dogs.py`.
