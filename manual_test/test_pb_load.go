// test if pb file is valid

package manual // changed from "manual_test" to "manual" to avoid conflicts with other packages

import (
	"log"
	"os"

	"RecommenderServer/schematree"
)

func main() {
	path := "geofabrik/netherlands-cleaned.tsv.schemaTree.typed.pb"

	f, err := os.Open(path)
	if err != nil {
		log.Fatalf("Failed to open file %s: %v", path, err)
	}
	defer f.Close()

	tree, err := schematree.LoadProtocolBufferFromReader(f)
	if err != nil {
		log.Fatalf("Failed to load schema tree: %v", err)
	}

	log.Printf("Successfully loaded schema tree with %d properties\n", tree.PropMap.Len())
}
