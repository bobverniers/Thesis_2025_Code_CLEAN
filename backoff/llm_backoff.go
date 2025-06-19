package backoff

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"

	"RecommenderServer/schematree"

	openai "github.com/sashabaranov/go-openai"
)

type LLMBackoff struct {
	tree    *schematree.SchemaTree
	client  *openai.Client
	context context.Context
}

func NewLLMBackoff(tree *schematree.SchemaTree) *LLMBackoff {
	apiKey := os.Getenv("OPENAI_API_KEY")
	if apiKey == "" {
		log.Fatal("Missing OPENAI_API_KEY environment variable")
	}

	fmt.Println("OPENAI_API_KEY is set:", apiKey[:6], "...(truncated)") // Debug print in correct scope

	client := openai.NewClient(apiKey)
	ctx := context.Background()

	return &LLMBackoff{
		tree:    tree,
		client:  client,
		context: ctx,
	}
}

func (b *LLMBackoff) CallWithCandidateList(inputTags []string, candidates []string) schematree.PropertyRecommendations {
	prompt := fmt.Sprintf(
		`You are helping tag restaurants in OpenStreetMap.
	
	Current input tags: %s
	
	From the following list of candidate tag keys:
	%s
	
	Select the 8 most relevant tags that are most likely to co-occur with the input, based on OpenStreetMap tagging conventions and real-world restaurant attributes.
	
	Return only the 8 tag keys, in order of relevance, one per line. Do not include explanations or any other text.`,
		strings.Join(inputTags, ", "),
		strings.Join(candidates, ", "),
	)

	resp, err := b.client.CreateChatCompletion(b.context, openai.ChatCompletionRequest{
		Model: openai.GPT3Dot5Turbo,
		Messages: []openai.ChatCompletionMessage{
			{Role: "user", Content: prompt},
		},
	})
	if err != nil {
		log.Printf("OpenAI API error: %v\n", err)
		return nil
	}

	content := resp.Choices[0].Message.Content
	lines := strings.Split(content, "\n")

	var finalRecs schematree.PropertyRecommendations
	seen := make(map[string]bool)

	// Step 1: Try to collect up to 10 tags from the LLM output
	for _, line := range lines {
		tag := strings.TrimSpace(strings.TrimLeft(line, "-.1234567890 "))
		if tag == "" || seen[tag] {
			continue
		}
		prop, ok := b.tree.PropMap.GetIfExisting(tag)
		if !ok {
			continue
		}

		finalRecs = append(finalRecs, schematree.RankedPropertyCandidate{
			Property: prop,
		})
		seen[tag] = true
		if len(finalRecs) == 10 {
			return finalRecs
		}
	}

	// Step 2: If fewer than 10, pad with remaining SchemaTree candidates
	for _, tag := range candidates {
		if len(finalRecs) == 10 {
			break
		}
		if seen[tag] {
			continue
		}
		prop, ok := b.tree.PropMap.GetIfExisting(tag)
		if !ok {
			continue
		}
		finalRecs = append(finalRecs, schematree.RankedPropertyCandidate{
			Property: prop,
		})
		seen[tag] = true
	}

	return finalRecs
}

// contains reports whether slice contains item
func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}
