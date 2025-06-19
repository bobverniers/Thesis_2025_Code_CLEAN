import osmium
import pandas as pd

# Bounding box for Antwerp: [min_lon, min_lat, max_lon, max_lat]
ANTWERP_BBOX = [4.33, 51.16, 4.52, 51.28]  # Roughly around Antwerp center

class RestaurantExtractor(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.restaurants = []

    def is_in_antwerp(self, lon, lat):
        min_lon, min_lat, max_lon, max_lat = ANTWERP_BBOX
        return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat

    def node(self, n):
        tags = n.tags
        if tags.get("amenity") == "restaurant" and self.is_in_antwerp(n.location.lon, n.location.lat):
            entry = {"osm_type": "node", "osm_id": n.id}
            for k, v in tags:
                entry[k] = v
            self.restaurants.append(entry)

    def way(self, w):
        tags = w.tags
        if tags.get("amenity") == "restaurant":
            try:
                lon = w.nodes[0].lon
                lat = w.nodes[0].lat
                if not self.is_in_antwerp(lon, lat):
                    return
            except:
                return
            entry = {"osm_type": "way", "osm_id": w.id}
            for k, v in tags:
                entry[k] = v
            self.restaurants.append(entry)

if __name__ == "__main__":
    pbf_path = "../geofabrik/belgium-latest.osm.pbf"
    output_csv = "restaurants_antwerp.csv"

    print("Extracting restaurants in Antwerp...")
    extractor = RestaurantExtractor()
    extractor.apply_file(pbf_path, locations=True)

    print(f"Found {len(extractor.restaurants)} restaurants.")
    df = pd.DataFrame(extractor.restaurants)
    df.to_csv(output_csv, index=False)
    print(f"Saved to {output_csv}")
