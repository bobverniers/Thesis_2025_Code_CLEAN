#!/usr/bin/env python3
"""
evaluation/score_model_a_with_hints.py

Evaluate Model A using a minimal hint (one ground-truth tag) alongside amenity and name.
Reads a CSV with at least these columns: name, hint_tag, and any ground-truth tag columns
(filtered to ≥4 tags).
"""

import pandas as pd
import subprocess
import os
import re
import argparse
from sklearn.metrics import precision_score, recall_score, f1_score

# -----------------------------------------------------------------------------
# Argument parsing
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Score Model A with partial hints (amenity, name, hint_tag) input."
)
parser.add_argument(
    "--csv", type=str, default="restaurants_with_hints.csv",
    help="Path to input CSV. Must include a 'hint_tag' column."
)
parser.add_argument(
    "--max", type=int, default=None,
    help="Max number of rows to evaluate (default: all)."
)
parser.add_argument(
    "--go-file", type=str, default="run_models.go",
    help="Path to the Go entrypoint for running Model A."
)
parser.add_argument(
    "--ignore-tags", nargs="*", default=["name", "amenity", "osm_id", "osm_type"],
    help="Tags/columns to ignore in ground truth."
)
args = parser.parse_args()

MODEL = "A"
GO_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def normalize(tag: str) -> str:
    """Basic normalization for tag strings."""
    return (tag
        .replace("contact:phone", "phone")
        .replace("contact:website", "website")
        .strip()
    )

# -----------------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------------
print(f"Loading data from {args.csv}…")
df = pd.read_csv(args.csv)
print(f"  → {len(df)} rows loaded.")

y_true, y_pred = [], []

# -----------------------------------------------------------------------------
# Iterate and score
# -----------------------------------------------------------------------------
for idx, row in df.iterrows():
    if args.max is not None and idx >= args.max:
        break

    name = str(row.get("name", "")).strip()
    hint = str(row.get("hint_tag", "")).strip()
    if not hint:
        continue  # skip if no hint available

    # Build input_tags: amenity, name, hint
    parts = ["amenity=restaurant"]
    if name:
        parts.append(name)
    parts.append(hint)
    input_tags = ",".join(parts)

    print(f"\n[{idx+1}/{len(df)}] {name} | hint: {hint}")
    cmd = [
        "go", "run", args.go_file,
        f"--input={input_tags}",
        f"--model={MODEL}"
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=GO_PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20
        )
    except Exception as e:
        print(f"  ERROR running Model A: {e}")
        continue

    # Parse predictions
    pred_tags = set()
    for line in proc.stdout.splitlines():
        m = re.search(r"\[\s*\d+\] (.+)", line)
        if m:
            t = normalize(m.group(1))
            if t not in args.ignore_tags:
                pred_tags.add(t)

    # Ground truth: drop metadata and hint
    truth = set(
        row
        .drop(labels=["osm_type", "osm_id", "name", "hint_tag"], errors="ignore")
        .dropna()
        .index
    )
    truth = {normalize(t) for t in truth if t not in args.ignore_tags}

    print(f"  Predicted: {sorted(pred_tags)}")
    print(f"  Truth:     {sorted(truth)}")

    if not truth:
        continue

    union = sorted(pred_tags.union(truth))
    y_true.append([t in truth for t in union])
    y_pred.append([t in pred_tags for t in union])

# -----------------------------------------------------------------------------
# Compute and report metrics
# -----------------------------------------------------------------------------
if not y_true:
    print("No examples evaluated.")
    exit(1)

# Flatten
y_true_flat = sum(y_true, [])
y_pred_flat = sum(y_pred, [])

print(f"\n=== Model A with Hints Evaluation ({args.csv}) ===")
print("Precision: %.3f" % precision_score(y_true_flat, y_pred_flat, zero_division=0))
print("Recall:    %.3f" % recall_score(y_true_flat, y_pred_flat, zero_division=0))
print("F1 Score:  %.3f" % f1_score(y_true_flat, y_pred_flat, zero_division=0))
