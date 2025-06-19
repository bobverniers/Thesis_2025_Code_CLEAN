#!/usr/bin/env python3
"""
Read restaurants_filtered.csv, extract the first GT tag as `hint_tag`,
and write out restaurants_with_hints.csv for downstream scoring.
"""
import random
random.seed(42)   # make random choice

import os
from utils import load_restaurants_csv, extract_random_tag_hint


# Input/Output filenames
INPUT_CSV  = "restaurants_filtered.csv"
OUTPUT_CSV = "restaurants_with_hints.csv"

def main():
    here = os.path.dirname(__file__)
    inp  = os.path.join(here, INPUT_CSV)
    out  = os.path.join(here, OUTPUT_CSV)

    print(f"Loading {inp}…")
    df = load_restaurants_csv(inp)

    print("Extracting random GT tag as hint_tag")

    df['hint_tag'] = extract_random_tag_hint(df)


    print(f"Writing {len(df)} rows with hints to {out}")
    df.to_csv(out, index=False)
    print("Done.")

if __name__ == "__main__":
    main()
