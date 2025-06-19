import pandas as pd

# Load CSV
df = pd.read_csv("ground_truth_1000.csv")

# Preview structure
print(f"Loaded {len(df)} rows")

# Check what the columns are
print("Columns:", df.columns.tolist())

# Print first example to verify
first = df.iloc[0]
name = first["name"]
amenity = first.get("amenity", "restaurant")
tags = set(first.drop(labels=["osm_type", "osm_id", "name"]).dropna().index)

print("\n=== First Entry ===")
print("Name:", name)
print("Amenity:", amenity)
print("Ground truth tags:", tags)
