"""Fetch the live Taiwan adoptable-dogs feed and write a normalized snapshot.

Run by .github/workflows/fetch_taiwan_dogs.yml on a schedule. Pure-Python
(requests + pandas) — deliberately no torch, so the Action stays fast. The site
scores the dogs itself (cached) when it loads the snapshot.

Usage:
    python scripts/fetch_taiwan_dogs.py          # fetch live feed
    python scripts/fetch_taiwan_dogs.py PATH.csv # normalize a local raw CSV instead
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

# Make `lib` importable whether run from repo root or scripts/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.data import (  # noqa: E402
    DATA_DIR, TAIWAN_CSV, TAIWAN_META, TAIWAN_SOURCE_JSON, normalize_taiwan,
)


def fetch_raw(local_csv: str | None = None) -> pd.DataFrame:
    if local_csv:
        print(f"Reading local raw CSV: {local_csv}")
        return pd.read_csv(local_csv)
    print(f"Fetching live feed: {TAIWAN_SOURCE_JSON}")
    try:
        resp = requests.get(TAIWAN_SOURCE_JSON, timeout=60)
    except requests.exceptions.SSLError:
        # The Taiwan gov server's TLS cert is non-compliant (missing a Subject
        # Key Identifier), which newer OpenSSL rejects. Scoped, logged exception
        # for this one known public-data endpoint — not a blanket verify=False.
        print("WARNING: TLS verify failed for data.moa.gov.tw (non-compliant gov "
              "cert). Retrying unverified for this known public endpoint only.")
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        resp = requests.get(TAIWAN_SOURCE_JSON, timeout=60, verify=False)
    resp.raise_for_status()
    return pd.DataFrame(resp.json())


def main():
    local_csv = sys.argv[1] if len(sys.argv) > 1 else None
    raw = fetch_raw(local_csv)
    print(f"Raw rows: {len(raw)}")

    dogs = normalize_taiwan(raw)
    print(f"Normalized adoptable dogs (with photo): {len(dogs)}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dogs.to_csv(TAIWAN_CSV, index=False)

    meta = {
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "n_dogs": int(len(dogs)),
        "n_shelters": int(dogs["shelter_name"].nunique()),
        "source": TAIWAN_SOURCE_JSON,
    }
    with open(TAIWAN_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"Wrote {TAIWAN_CSV} ({meta['n_dogs']} dogs, {meta['n_shelters']} shelters)")


if __name__ == "__main__":
    main()
