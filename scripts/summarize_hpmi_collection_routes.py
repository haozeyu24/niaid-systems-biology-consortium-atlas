#!/usr/bin/env python3

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "papers" / "sources" / "hpmi" / "manifest.csv"


def main() -> int:
    rows = list(csv.DictReader(MANIFEST_PATH.open(encoding="utf-8")))
    route_counter: Counter[str] = Counter()
    year_counter: Counter[str] = Counter()

    for row in rows:
        route_counter.update((row.get("collection_route") or "").split(";"))
        year_counter.update([row.get("year", "")])

    print(f"rows: {len(rows)}")
    print("collection_route counts:")
    for route, count in route_counter.most_common():
        if route:
            print(f"  {route}: {count}")
    print("top years:")
    for year, count in year_counter.most_common(10):
        if year:
            print(f"  {year}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
