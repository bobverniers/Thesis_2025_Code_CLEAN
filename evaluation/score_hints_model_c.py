#!/usr/bin/env python3
"""
evaluation/score_hints_model_c.py

Evaluate Model C (SchemaTree + LLM backoff) using a minimal hint (one ground-truth tag) alongside the original `restaurant` tag format.
Reads a CSV with at least these columns: name, hint_tag, and any ground-truth tag columns (filtered to ≥4 tags).
"""

import pandas as pd
import subprocess
import os
import re
import argparse
from sklearn.metrics import precision_score, recall_score, f1_score

# -----------------------------------------------------------------------------
# CLI arguments
# -----------------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Score Model C with partial hints (restaurant, name, hint_tag) input."
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
    help="Path to the Go entrypoint for running Model C."
)
parser.add_argument(
    "--ignore-tags", nargs="*", default=["name", "restaurant", "osm_id", "osm_type"],
    help="Tags/columns to ignore in ground truth."
)
args = parser.parse_args()

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
MODEL = "C"
GO_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def normalize(tag: str) -> str:
    """Normalize tag strings to comparable form."""
    return (tag.replace("contact:phone", "phone")
              .replace("contact:website", "website").strip())

# -----------------------------------------------------------------------------
# Load CSV
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

    name = row["name"]
    if not isinstance(name, str) or len(name.strip()) == 0:
        continue

    hint = row.get("hint_tag", "").strip()
    if not hint:
        continue  # skip if no hint available

    print(f"\n[{idx+1}/{len(df)}] {name} | hint: {hint}")
    input_tags = f"restaurant,{name},{hint}"
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
            timeout=30
        )
    except Exception as e:
        print(f"ERROR running Model C: {e}")
        continue

    # Extract LLM re-ranked tags
    pred_tags = set()
    llm_section = False
    count = 0
    for line in proc.stdout.splitlines():
        if "LLM re-ranked recommendations:" in line:
            llm_section = True
            continue
        if llm_section:
            if count >= 8:
                break
            match = re.search(r"\[\s*\d+\]\s*(\S+)", line)
            if match:
                tag = normalize(match.group(1))
                if tag not in args.ignore_tags:
                    pred_tags.add(tag)
                    count += 1

    # Extract ground truth tags
    truth = set(
        row
          .drop(labels=["osm_type", "osm_id", "name", "hint_tag"], errors="ignore")
          .dropna()
          .index
    )
    truth = {normalize(t) for t in truth if t not in args.ignore_tags}

    print("Model C predicted tags:", sorted(pred_tags))
    print("Ground truth tags:   ", sorted(truth))

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

print(f"\n=== Model C with Hints Evaluation ({args.csv}) ===")
print("Precision: %.3f" % precision_score(y_true_flat, y_pred_flat, zero_division=0))
print("Recall:    %.3f" % recall_score(y_true_flat, y_pred_flat, zero_division=0))
print("F1 Score:  %.3f" % f1_score(y_true_flat, y_pred_flat, zero_division=0))
