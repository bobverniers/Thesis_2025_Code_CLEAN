package manual_test

import (
	"log"
	"os"
	"sort"
	"testing"

	"RecommenderServer/backoff"
	ST "RecommenderServer/schematree"
)

var treePathTyped = "../geofabrik/netherlands-cleaned.tsv.schemaTree.typed.pb"

// Model B :  using DeleteLowFrequencyProperty backoff strategy on OSM-based Netherlands data.
func TestDeleteLowFrequencyBackoff(t *testing.T) {
	f, err := os.Open(treePathTyped)
	if err != nil {
		log.Panicf("Error opening schema tree: %v", err)
	}
	defer f.Close()

	tree, err := ST.LoadProtocolBufferFromReader(f)
	if err != nil {
		log.Panicf("Error loading schema tree: %v", err)
	}

	pMap := tree.PropMap

	// take real properties from schema tree
	prop1, ok1 := pMap.GetIfExisting("cycleway:surface")
	prop2, ok2 := pMap.GetIfExisting("barrier:material")

	if !(ok1 && ok2) {
		t.Fatal("Properties not found in propMap. Make sure your tags exist in the data.")
	}

	props := ST.IList{prop1, prop2}

	// Create the backoff strategy (Model B)
	backoffStrategy := backoff.NewBackoffDeleteLowFrequencyItems(tree, 4, backoff.StepsizeLinear, backoff.MakeMoreThanInternalCondition(2))

	recs := backoffStrategy.Recommend(props)

	const threshold = 0.1

	// Sort by descending probability
	sort.Slice(recs, func(i, j int) bool {
		return recs[i].Probability > recs[j].Probability
	})

	count := 0
	for _, r := range recs {
		if r.Probability > threshold {
			log.Printf("Recommended: %s (%.2f)", *r.Property.Str, r.Probability)
			count++
			if count >= 50 {
				break
			}
		}
	}

	if count == 0 {
		t.Log("No recommendations above threshold.")
	}
}
