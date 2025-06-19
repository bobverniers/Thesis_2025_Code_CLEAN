// Model A no backoff strategy

/* so i can run run MODEL B 

package main

import (
	"log"
	"os"
	"sort"
	"testing"

	"RecommenderServer/schematree"

	"github.com/stretchr/testify/assert"
)

func TestRecommend(t *testing.T) {
	// Load the schema tree
	f, err := os.Open("../geofabrik/netherlands-cleaned.tsv.schemaTree.typed.pb")
	if err != nil {
		t.Fatalf("Failed to open .pb file: %v", err)
	}
	defer f.Close() // close file when done

	tree, err := schematree.LoadProtocolBufferFromReader(f)
	if err != nil {
		t.Fatalf("Failed to load schema tree: %v", err)
	}
	assert.NotNil(t, tree, "SchemaTree should not be nil")

	// Use a real property for recommendation
	inputProps := []string{"bus_stop"}
	recommendations := tree.Recommend(inputProps, nil)

	// Sort recommendations by probability (highest first)
	sort.Slice(recommendations, func(i, j int) bool {
		return recommendations[i].Probability > recommendations[j].Probability
	})

	// Log only the top 10 non-zero recommendations
	nonZero := 0
	for _, rec := range recommendations {
		if rec.Probability > 0.0 {
			log.Printf("Recommended: %s (%.2f)", *rec.Property.Str, rec.Probability)
			nonZero++
			if nonZero >= 10 {
				break
			}
		}
	}

	assert.Greater(t, nonZero, 0, "Expected at least one non-zero recommendation")
}

