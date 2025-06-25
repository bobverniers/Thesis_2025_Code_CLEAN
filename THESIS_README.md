
# Thesis: Hybrid Tag Recommendation for OpenStreetMap  
**Author**: Bob Verniers  
**Supervisor**: Michael Cochez  

---

This thesis explores a hybrid recommendation system combining:

- **SchemaTree (ST)** — a co-occurrence-based tag recommender
- **LLM re-ranking (OpenAI GPT-3.5)** — to improve contextual tag recommendations

Models:

- **Model A**: SchemaTree (no backoff) — baseline
- **Model C**: SchemaTree top-30 + LLM re-ranking — hybrid

Training: Netherlands OSM restaurants  
Testing: Antwerp restaurants (822 entities)  
Ground Truth tags extracted from OpenStreetMap (`restaurants_antwerp.csv`)

---

## Pre-trained model

The SchemaTree `.pb` model (`geofabrik/netherlands-cleaned.tsv.schemaTree.typed.pb`)  
was trained offline on Netherlands OSM data (`geofabrik/netherlands-cleaned.tsv`)

No additional training step is needed to reproduce these experiments.  
The pre-trained `.pb` model is included in this repository.

## Steps to create the .pb model yourself. NB: This step is not necessary, as the .pb model is already included. However, if you want to retrain it yourself, you can follow these steps:

1. You can download the latest Netherlands .osm.pbf file.
Download from: https://download.geofabrik.de/europe/netherlands.html
Save as: geofabrik/netherlands-latest.osm.pbf

2. Open osm_to_tsv.ipynb , change PBF path; PBF_path = "geofabrik/netherlands-latest.osm.pbf"

3. Run the notebook which will output geofabrik/netherlands-latest.tsv

4. Clean the TSV file, to remove rows with one tag run this in terminal:
```
awk 'NF > 1' geofabrik/netherlands-latest.tsv > geofabrik/netherlands-cleaned.tsv
```
5. Train the SchemaTree model 

```
go run RecommenderServer/train_schema_tree.go \
  --input geofabrik/netherlands-cleaned.tsv \
  --output geofabrik/netherlands-cleaned.tsv.schemaTree.typed.pb
```

6. This will output: geofabrik/netherlands-cleaned.tsv.schemaTree.typed.pb

You can run all experiments with this pb model. 
---

## Test CSV Files: The csv files needed for evaluation are already included in this repository.

- `evaluation/restaurants_antwerp.csv`  
- `evaluation/restaurants_with_hints.csv`  

If you want to recreate `restaurants_antwerp.csv` yourself:
1. Download Belgium PBF:https://download.geofabrik.de/europe/belgium.html
Save as: geofabrik/belgium-latest.osm.pbf

2. Run the extractor script:
```
python evaluation/antwerp_extract_restaurants.py
```
This will output: evaluation/restaurants_antwerp.csv

3. If you want to recreate restaurants_with_hints.csv:

Filter restaurants with 4 or more ground truth tags:
```
python evaluation/filter_gt3.py
```

This will create: evaluation/restaurants_filtered.csv

Then generate restaurants_with_hints.csv with the following command.

```
python evaluation/add_hints.py
```

For full details, see the thesis Methodology section.

## Setup

**This guide applies for Mac Users**  

### Install dependencies:


Assure that homebrew is installed

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

```
brew install go  
brew install python  
pip install pandas openai scikit-learn
```

### Clone the repo:

```
git clone https://github.com/bobverniers/Thesis_2025_Code_CLEAN.git
cd Thesis_2025_Code_CLEAN
```

---

### Add your OpenAI API key (for Model C):


```
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

You can generate your own key here: https://platform.openai.com/account/api-keys

---

## Running the experiments:

### Test both models on a single entity:

```
go run run_models.go --input "amenity=restaurant,La Thai" --model A
go run run_models.go --input "amenity=restaurant,La Thai" --model C
```

---

### Reproduce evaluation results (from thesis):

```
cd evaluation
```
## Model A 

```
python score_model_a.py --csv restaurants_antwerp.csv --max 822
```

## Model C

```
python score_model_c.py --csv restaurants_antwerp.csv --max 822
```

---

### Run Model A with hint tag:

```
python score_hints_model_a.py --csv restaurants_with_hints.csv --max 523
```

---

### Run Model C with hint tag:

```
python score_hints_model_c.py --csv restaurants_with_hints.csv --max 523
```

---

