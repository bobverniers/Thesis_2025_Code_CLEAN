import osmium
import pandas as pd

class RestaurantExtractor(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.restaurants = []

    def extract_tags(self, tags, elem_type, elem_id):
        name = tags.get("name")
        if name:
            self.restaurants.append({
                "osm_type": elem_type,
                "osm_id": elem_id,
                "name": name,
                "tags": dict(tags)
            })

    def node(self, n):
        if n.tags.get("amenity") == "restaurant":
            self.extract_tags(n.tags, "node", n.id)

    def way(self, w):
        if w.tags.get("amenity") == "restaurant":
            self.extract_tags(w.tags, "way", w.id)

    def relation(self, r):
        if r.tags.get("amenity") == "restaurant":
            self.extract_tags(r.tags, "relation", r.id)

# Initialize handler
handler = RestaurantExtractor()
handler.apply_file("restaurants.osm.pbf")

# Convert to DataFrame
df = pd.DataFrame(handler.restaurants)

# Expand the tag dict
tags_df = df["tags"].apply(pd.Series)
full_df = pd.concat([df.drop(columns=["tags"]), tags_df], axis=1)

# Sample 1000 restaurants
sample = full_df.sample(n=1000, random_state=42)
sample.to_csv("ground_truth_1000.csv", index=False)

print("Saved sample of 1000 restaurants to ground_truth_1000.csv")
