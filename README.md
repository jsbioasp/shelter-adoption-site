# Shelter Adoption ML — Site

A Streamlit site for the course's shelter-adoption models and findings. Upload a
dog's data, photo, or both for a live prediction; browse real adoptable dogs from
Taiwan's open-data feed; read the experiments behind the numbers.

This is the **capstone reference site** for Module 7. Students co-own it: each
person owns one or two sections and ships changes via pull requests to `main`.

## Run it locally

```bash
cd site
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

First launch downloads the ConvNeXt-Tiny weights (~110 MB) for photo scoring.

## Deploy (Streamlit Community Cloud)

1. Push this `site/` directory's contents as the **root** of a GitHub repo.
2. On [share.streamlit.io](https://share.streamlit.io), point a new app at the repo,
   entry file `streamlit_app.py`.
3. Merge a PR to `main` → the app auto-redeploys. That's the whole loop.

> The `.github/workflows/` folder must sit at the **repo root** to run — which it
> does once `site/` is the repo root.

## Layout

```
streamlit_app.py        # entry — wires the 5 sections into the sidebar nav
sections/               # one file per student-owned section
  motivation.py         #   🎯 Landing / Motivation
  datasets.py           #   📊 Datasets & Experiments
  results.py            #   🏆 Results
  models_ui.py          #   🔮 Try the Models (data / image / data+image)
  discover.py           #   🔍 Discover Dogs (live Taiwan feed)
lib/                    # shared infrastructure (not section-owned)
  models.py             #   model load + 3 scoring modes (vendored architectures)
  features.py           #   form inputs / Taiwan rows -> SHARED_6 vector
  data.py               #   findings constants + Taiwan snapshot loader
models/                 # m06_ensemble.pkl (1 MB) + m06_tabular_only.pkl (59 KB)
data/                   # taiwan_dogs.csv snapshot (refreshed by the Action)
scripts/fetch_taiwan_dogs.py   # the ETL the Action runs
.github/workflows/fetch_taiwan_dogs.yml   # daily snapshot refresh
```

## The models

- **Data-only**: a 5-seed `FlatMLP` ensemble on 6 demographic features (SHARED_6),
  test AUC ≈ 0.654.
- **Photo + data**: a 5-seed multi-task model (ConvNeXt-Tiny photo trunk + adopt
  head + `is_young` aux head), test AUC ≈ 0.698.

Both are tiny and run on CPU. The model architectures are vendored into
`lib/models.py` so the site is self-contained — it does not import the research
code in `modules/` or `trial/`.

## The live Taiwan data

`scripts/fetch_taiwan_dogs.py` pulls the Taiwan Ministry of Agriculture
adoptable-animals feed ([dataset 85903](https://data.gov.tw/en/datasets/85903)),
filters to adoptable dogs-with-photos, and writes `data/taiwan_dogs.csv`. The
GitHub Action runs it daily and commits any change; Streamlit redeploys on that
commit. Photos are referenced by URL, so the snapshot stays small.

## Co-ownership workflow

- Section owners edit only their `sections/<name>.py`.
- Shared changes to `lib/` get a quick review (they affect everyone).
- Open a PR → merge to `main` → site redeploys. Keep sections independent so PRs
  don't collide.

## Contributors:
- Neo Chou