import pandas as pd
import subprocess
import os
import re
import argparse
from sklearn.metrics import precision_score, recall_score, f1_score

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--csv", type=str, default="ground_truth_1000.csv", help="Path to input CSV file")
parser.add_argument("--max", type=int, default=5, help="Max number of rows to evaluate")
args = parser.parse_args()

# Config
MODEL = "A"
GO_FILE = "run_models.go"
CSV_PATH = args.csv
GO_PROJECT_DIR = os.path.abspath("..")
IGNORE_TAGS = {"name", "name.1", "amenity"}
MAX_ROWS = args.max

# Normalization helper
def normalize(tag):
    return tag.replace("contact:phone", "phone").replace("contact:website", "website")

# Load the CSV
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} rows from {CSV_PATH}")

y_true = []
y_pred = []

for idx, row in df.iterrows():
    if idx >= MAX_ROWS:
        break
    name = row.get("name", "")
    if not isinstance(name, str) or len(name.strip()) == 0:
        continue

    print(f"\n[{idx+1}/{len(df)}] {name}")
    name = row.get("name", "").strip()
    input_tags = f"amenity=restaurant,{name}" if name else "amenity=restaurant"

    cmd = ["go", "run", GO_FILE, f"--input={input_tags}", f"--model={MODEL}"]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15,
            cwd=GO_PROJECT_DIR
        )
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        continue
    except Exception as e:
        print(f"ERROR: {e}")
        continue

    output = result.stdout

    # Extract predicted tags
    pred_tags = set()
    for line in output.splitlines():
        match = re.search(r"\[\s*\d+\] (.+)", line)
        if match:
            tag = match.group(1).strip()
            if tag not in IGNORE_TAGS:
                pred_tags.add(normalize(tag))

    # Extract ground truth tags
    truth_tags = set(
        row.drop(labels=["osm_type", "osm_id", "name"], errors="ignore").dropna().index
    )
    truth_tags = {normalize(t) for t in truth_tags if t not in IGNORE_TAGS}

    print("Model A predicted tags:", sorted(pred_tags))
    print("Ground truth tags:     ", sorted(truth_tags))

    if not truth_tags:
        continue

    all_tags = sorted(pred_tags.union(truth_tags))
    y_true_vec = [tag in truth_tags for tag in all_tags]
    y_pred_vec = [tag in pred_tags for tag in all_tags]

    y_true.append(y_true_vec)
    y_pred.append(y_pred_vec)

# Final scores
y_true_flat = sum(y_true, [])
y_pred_flat = sum(y_pred, [])

print(f"\n=== Model A Evaluation ({CSV_PATH}, first {MAX_ROWS} rows) ===")
print("Precision: %.3f" % precision_score(y_true_flat, y_pred_flat, zero_division=0))
print("Recall:    %.3f" % recall_score(y_true_flat, y_pred_flat, zero_division=0))
print("F1 Score:  %.3f" % f1_score(y_true_flat, y_pred_flat, zero_division=0))
