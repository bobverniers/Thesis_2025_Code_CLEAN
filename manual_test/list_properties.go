// manual_test/list_properties.go
package manual // changed from "manual_test" to "manual" to avoid conflicts with other packages

import (
	"fmt"
	"log"
	"os"

	"RecommenderServer/schematree"
)

func main() {
	f, err := os.Open("/Users/bobi/Desktop/Thesis/RecommenderServer/geofabrik/netherlands-cleaned.tsv.schemaTree.typed.pb")
	if err != nil {
		log.Fatalf("Could not open file: %v", err)
	}
	defer f.Close()

	tree, err := schematree.LoadProtocolBufferFromReader(f)
	if err != nil {
		log.Fatalf("Could not load schema tree: %v", err)
	}

	for _, prop := range tree.AllProperties() {
		fmt.Println(prop)
	}
}
