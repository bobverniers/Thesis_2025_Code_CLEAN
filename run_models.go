package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"strings"

	"RecommenderServer/schematree"
	"RecommenderServer/strategy"
)

func main() {
	// CLI flags
	inputFlag := flag.String("input", "", "Comma-separated list of input tags (e.g. 'restaurant,La Thai')")
	modelFlag := flag.String("model", "A", "Model to run: A or C")
	flag.Parse()

	if *inputFlag == "" {
		log.Fatal("Please provide input tags using --input")
	}

	// Parse input tags
	inputTags := strings.Split(*inputFlag, ",")

	// Load SchemaTree model
	modelPath := "geofabrik/netherlands-cleaned.tsv.schemaTree.typed.pb"
	file, err := os.Open(modelPath)
	if err != nil {
		log.Fatalf("could not open model file: %v", err)
	}
	defer file.Close()

	model, err := schematree.LoadProtocolBufferFromReader(file)
	if err != nil {
		log.Fatalf("could not load SchemaTree model: %v", err)
	}

	// Create instance from input
	instance := schematree.NewInstanceFromInput(inputTags, nil, model, true)

	// Select model
	var wf *strategy.Workflow
	switch strings.ToUpper(*modelFlag) {
	case "A":
		wf = strategy.MakeModelAWorkflow(model)
	case "C":
		wf = strategy.MakeModelCWorkflow(model)
	default:
		log.Fatalf("Unknown model: %s", *modelFlag)
	}

	fmt.Println("Using model:", *modelFlag)

	// Run workflow
	recs := wf.Recommend(instance)

	// Print results
	fmt.Printf("\nTop 10 recommended tags (Model %s):\n", strings.ToUpper(*modelFlag))
	for i, rec := range recs {
		if i >= 10 {
			break
		}
		fmt.Printf("[ %d] %s\n", i+1, *rec.Property.Str)
	}

}
