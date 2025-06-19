#!/usr/bin/env python3
"""
evaluation/filter_gt3.py

Filter restaurants_with_gt3.csv to only those rows
with ≥4 ground-truth tags (excluding name, amenity, osm_id, osm_type).
Outputs restaurants_filtered.csv.
"""

import os
from utils import load_restaurants_csv, filter_by_min_tags

# Input/Output filenames
INPUT_CSV  = "restaurants_antwerp.csv"
OUTPUT_CSV = "restaurants_filtered.csv"


def main():
    here = os.path.dirname(__file__)
    inp  = os.path.join(here, INPUT_CSV)
    out  = os.path.join(here, OUTPUT_CSV)

    print(f"Loading {inp}…")
    df = load_restaurants_csv(inp)

    print("Applying ≥4-tag filter…")
    filtered = filter_by_min_tags(df, min_tags=4)

    print(f"Writing {len(filtered)} rows to {out}")
    filtered.to_csv(out, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
