# compute_gt_avg.py
import pandas as pd

# Load the CSV
df = pd.read_csv("restaurants_antwerp.csv")

# Define columns to ignore (metadata)
ignore = {"name", "amenity", "osm_id", "osm_type"}

# Compute tag counts per row
counts = df.apply(lambda row: len([
    col for col in row.index 
    if col not in ignore and pd.notna(row[col])
]), axis=1)

# Print results
print(f"Average number of ground-truth tags per row: {counts.mean():.2f}")
print(f"Minimum tags: {counts.min()}, Maximum tags: {counts.max()}")
