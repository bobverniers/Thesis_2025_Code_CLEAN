import pandas as pd
import subprocess
import os
import re
import argparse
from sklearn.metrics import precision_score, recall_score, f1_score

# CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument("--csv", default="ground_truth_1000.csv", help="Path to CSV file")
parser.add_argument("--max", type=int, default=5, help="Max number of rows to evaluate")
args = parser.parse_args()

# Config
MODEL = "C"
GO_FILE = "run_models.go"
CSV_PATH = args.csv
MAX_ROWS = args.max
GO_PROJECT_DIR = os.path.abspath("..")
IGNORE_TAGS = {"name", "name.1", "amenity"}

# Normalization helper
def normalize(tag):
    return tag.replace("contact:phone", "phone").replace("contact:website", "website")

# Load CSV
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} rows from {CSV_PATH}")

y_true = []
y_pred = []

for idx, row in df.iterrows():
    if idx >= MAX_ROWS:
        break

    name = row["name"]
    if not isinstance(name, str) or len(name.strip()) == 0:
        continue

    print(f"\n[{idx+1}/{len(df)}] {name}")
    input_tags = f"restaurant,{name}"
    cmd = ["go", "run", GO_FILE, f"--input={input_tags}", f"--model={MODEL}"]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
            cwd=GO_PROJECT_DIR
        )
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        continue
    except Exception as e:
        print(f"ERROR: {e}")
        continue

    output = result.stdout

    # Extract LLM re-ranked tags
    pred_tags = set()
    llm_section = False
    llm_lines_collected = 0
    for line in output.splitlines():
        if "LLM re-ranked recommendations:" in line:
            llm_section = True
            continue
        if llm_section:
            if llm_lines_collected >= 8:
                break
            if match := re.search(r"\[\s*\d+\]\s*(\S+)", line):
                tag = normalize(match.group(1).strip())
                if tag not in IGNORE_TAGS:
                    pred_tags.add(tag)
                    llm_lines_collected += 1
            elif line.strip() == "":
                break

    # Extract ground truth
    truth_tags = set(
        row.drop(labels=["osm_type", "osm_id", "name"], errors="ignore").dropna().index
    )
    truth_tags = {normalize(t) for t in truth_tags if t not in IGNORE_TAGS}

    print("Model C predicted tags:", sorted(pred_tags))
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

print(f"\n=== Model C Evaluation ({CSV_PATH}, first {MAX_ROWS} rows) ===")
print("Precision: %.3f" % precision_score(y_true_flat, y_pred_flat, zero_division=0))
print("Recall:    %.3f" % recall_score(y_true_flat, y_pred_flat, zero_division=0))
print("F1 Score:  %.3f" % f1_score(y_true_flat, y_pred_flat, zero_division=0))
