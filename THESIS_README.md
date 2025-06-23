
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

---

## Setup

### Install dependencies:

**Mac/Linux:**  

```bash
brew install go  
brew install python  
pip install pandas openai  
```

**Windows:**  

- Download and install Go: https://go.dev/dl/  
- Download and install Python 3: https://www.python.org/downloads/windows/  
- In Command Prompt:  

```
pip install pandas openai  
```

---

### Clone the repo:

```
git clone https://github.com/bobverniers/Thesis_2025_Code_CLEAN.git
cd Thesis_2025_Code_CLEAN
```

---

### Add your OpenAI API key (for Model C):

**Mac/Linux Terminal:**  
```
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

**Windows CMD:**  
```
set OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
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

python score_model_a.py --csv restaurants_antwerp.csv --max 822
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

## Notes:

- Always run Go commands from the repo root folder:  
`cd Thesis_2025_Code_CLEAN`
