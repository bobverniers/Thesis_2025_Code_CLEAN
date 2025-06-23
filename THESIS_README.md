Thesis: Hybrid Tag Recommendation for OpenStreetMap
Author: Bob Verniers
Supervisor: Michael Cochez


This thesis explores a hybrid recommendation system combining:

SchemaTree (ST), a co-occurrence-based tag recommender

LLM re-ranking (OpenAI GPT-3.5), to improve contextual tag recommendations

Model A: SchemaTree (no backoff) — baseline

Model C: SchemaTree top-30 + LLM re-ranking — hybrid

Training: Netherlands OSM restaurants

Testing: Antwerp restaurants (822 entities)

Ground Truth tags extracted from OpenStreetMap (see restaurants_antwerp.csv).

NOTE:
The SchemaTree .pb model (geofabrik/netherlands-cleaned.tsv.schemaTree.typed.pb)
was trained offline on Netherlands OSM data (from geofabrik/netherlands-cleaned.tsv)

No additional training step is needed to reproduce these experiments.
The pre-trained .pb model is included in this repository.


Step 1: To run this evaluation pipeline you need to download the following (run in terminal):

brew install go
brew install python
pip install pandas openai


Step 2: Clone the repo 
git clone https://github.com/bobverniers/Thesis_2025_Code_CLEAN.git
cd Thesis_2025_Code_CLEAN


Step 3: add your OpenAI API key (for Model C)

Before running Model C, you need to set your own OpenAI API key in your terminal:

export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

generate your own at https://platform.openai.com/account/api-keys


Step 4: verify it works by running both models on a single entity. 

Run from repository root, cd ..

go run run_models.go --input "amenity=restaurant,La Thai" --model A
go run run_models.go --input "amenity=restaurant,La Thai" --model C

Step 5: To reproduce the evaluation results from the thesis Run Model A and C 

cd evaluation
python score_model_a.py --csv restaurants_antwerp.csv --max 822

python score_model_c.py --csv restaurants_antwerp.csv --max 822

Step 6: Run Model A with hint_tag
python score_hints_model_a.py --csv restaurants_with_hints.csv --max 523


Step 7: Run Model C with hint_tag
python score_hints_model_c.py --csv restaurants_with_hints.csv --max 523