package strategy

// This file is responsible for holding presets for strategy definitions.

import (
	"RecommenderServer/backoff"
	"RecommenderServer/schematree"
	"fmt"
)

// Helper method to create a condition that always evaluates to true.
func MakeAlwaysCondition() Condition {
	return func(asm *schematree.Instance) bool {
		return true
	}
}

// Not needed anylonger
// Helper method to create the above-threshold condition.
func MakeAboveThresholdCondition(threshold int) Condition {
	return func(asm *schematree.Instance) bool {
		return len(asm.Props) > threshold
	}
}

func MakeBelowThresholdCondition(threshold int) Condition {
	return func(asm *schematree.Instance) bool {
		return len(asm.Props) < threshold
	}
}

// Not needed anylonger
// Helper Method to create too-many-recommendations-condition: When the standard recommender returns more than count many recommendations the condition is true, else false
func MakeTooManyRecommendationsCondition(threshold int) Condition {
	return func(asm *schematree.Instance) bool {
		recommendation := asm.CalcRecommendations()
		return len(recommendation) > threshold
	}
}

// Helper Method to create too-few-recommendations-condition: When the standard recommender returns less than count many recommendations the condition is true, else false
func MakeTooFewRecommendationsCondition(threshold int) Condition {
	return func(asm *schematree.Instance) bool {
		recommendation := asm.CalcRecommendations()
		return len(recommendation) < threshold
	}
}

// Helper Method to create too-unlikely-recommendations-condition: When the standard recommender returns a recommendation where the top 10 has lower probability than threshhold (in decimal percentage eg 0.5)
func MakeTooUnlikelyRecommendationsCondition(threshold float32) Condition {
	return func(asm *schematree.Instance) bool {
		recommendation := asm.CalcRecommendations()
		return recommendation.Top10AvgProbibility() < threshold
	}
}

// Helper method to create the direct SchemaTree procedure call.
//func MakeDirectProcedure(tree *schematree.SchemaTree) Procedure {
//	return func(asm *schematree.Instance) schematree.PropertyRecommendations {
//		return tree.RecommendProperty(asm.Props)
//	}
//}

// Helper method to create the direct SchemaTree procedure call.
func MakeAssessmentAwareDirectProcedure() Procedure {
	return func(asm *schematree.Instance) schematree.PropertyRecommendations {
		return asm.CalcRecommendations()
	}
}

// Helper method to create the 'deletelowfrequency' backoff procedure.
func MakeDeleteLowFrequencyProcedure(tree *schematree.SchemaTree, parExecs int, stepsize backoff.StepsizeFunc, condition backoff.InternalCondition) Procedure {
	b := backoff.NewBackoffDeleteLowFrequencyItems(tree, parExecs, stepsize, condition)
	return func(asm *schematree.Instance) schematree.PropertyRecommendations {
		return b.Recommend(asm.Props)
	}
}

// Helper method to create the 'splitproperty' backoff procedure.
func MakeSplitPropertyProcedure(tree *schematree.SchemaTree, splitter backoff.SplitterFunc, merger backoff.MergerFunc) Procedure {
	b := backoff.NewBackoffSplitPropertySet(tree, splitter, merger)
	return func(asm *schematree.Instance) schematree.PropertyRecommendations {
		return b.Recommend(asm.Props)
	}
}

// MakePresetWorkflow : Build a preset strategy that is hard-coded.
func MakePresetWorkflow(name string, tree *schematree.SchemaTree) *Workflow {
	wf := Workflow{}

	switch name {

	// Will always call the deleteLowFrequency backoff algorithm.
	case "deletelowfrequency":
		wf.Push(
			MakeAlwaysCondition(),
			MakeDeleteLowFrequencyProcedure(tree, 4, backoff.StepsizeProportional, backoff.MakeMoreThanInternalCondition(10)),
			"always run deletelowfrequency with 4 parallel processes",
		)

	case "best":
		wf.Push(
			MakeTooFewRecommendationsCondition(1),
			MakeDeleteLowFrequencyProcedure(tree, 4, backoff.StepsizeLinear, backoff.MakeMoreThanInternalCondition(4)),
			"run deletelowfrequency with 4 parallel processes",
		)
		wf.Push(
			MakeAlwaysCondition(),
			MakeAssessmentAwareDirectProcedure(), //MakeDirectProcedure(tree),
			"always run direct algorithm",
		)

	// Will always call the splitProperty backoff algorithm.
	case "splitproperty":
		wf.Push(
			MakeAboveThresholdCondition(2),
			MakeSplitPropertyProcedure(tree, backoff.EverySecondItemSplitter, backoff.MaxMerger),
			"with 3 or more properties run splitproperty",
		)
		wf.Push(
			MakeAlwaysCondition(),
			MakeAssessmentAwareDirectProcedure(), //MakeDirectProcedure(tree),
			"default to running direct algorithm",
		)

	// Test to show that recommendations can be called on conditions, and that a
	// assessment-aware procedure can use those recommendations.
	case "toofewrecommendations":
		wf.Push(
			MakeTooFewRecommendationsCondition(10),
			MakeDeleteLowFrequencyProcedure(tree, 4, backoff.StepsizeProportional, backoff.MakeMoreThanInternalCondition(10)),
			"if less than 10 recommendations are generated, run the deletelowfrequency backoff",
		)
		wf.Push(
			MakeAlwaysCondition(),
			MakeAssessmentAwareDirectProcedure(), //makeAssessmentAwareDirectProcedure(),
			"default to direct algorithm, but use assessment cache if possible",
		)

	// Calls the schematree core algorithm directly.
	case "direct":
		wf.Push(
			MakeAlwaysCondition(),
			MakeAssessmentAwareDirectProcedure(), //MakeDirectProcedure(tree),
			"always run direct algorithm",
		)
	default:
		panic("Given strategy name does not exist as a preset.")
	}

	return &wf
}

func MakeModelCWorkflow(tree *schematree.SchemaTree) *Workflow {
	wf := Workflow{}

	wf.Push(
		MakeAlwaysCondition(),
		func(asm *schematree.Instance) schematree.PropertyRecommendations {
			// Step 1: Get top N SchemaTree recommendations
			schemaRecs := asm.CalcRecommendations()
			if len(schemaRecs) > 30 {
				schemaRecs = schemaRecs[:30]
			}

			// Debug: Print top SchemaTree recommendations
			fmt.Println("Top SchemaTree recommendations:")
			for i, rec := range schemaRecs {
				fmt.Printf("  [%d] %s (%.2f%%)\n", i+1, *rec.Property.Str, rec.Probability*100)
			}

			// Step 2: Extract candidate tag keys
			var candidateTags []string
			for _, rec := range schemaRecs {
				candidateTags = append(candidateTags, *rec.Property.Str)
			}

			// Step 3: Collect input tags
			var inputStrings []string
			for _, prop := range asm.Props {
				inputStrings = append(inputStrings, *prop.Str)
			}

			// Step 4: Call LLM to reorder candidate tags
			llm := backoff.NewLLMBackoff(tree)
			reordered := llm.CallWithCandidateList(inputStrings, candidateTags)

			// Debug: Print LLM-reordered tags
			fmt.Println("\nLLM re-ranked recommendations:")
			for i, rec := range reordered {
				fmt.Printf("  [%d] %s\n", i+1, *rec.Property.Str)
			}

			// Step 5: Return only the top 8 tags
			if len(reordered) > 8 {
				reordered = reordered[:8]
			}
			return reordered
		},
		"SchemaTree top-N + LLM re-ranking, returning top 8",
	)

	return &wf

}

// MakeModelAWorkflow: SchemaTree → Always use top 10 recommendations
func MakeModelAWorkflow(tree *schematree.SchemaTree) *Workflow {
	wf := Workflow{}

	wf.Push(
		MakeAlwaysCondition(),
		func(asm *schematree.Instance) schematree.PropertyRecommendations {
			// Get SchemaTree recommendations
			schemaRecs := asm.CalcRecommendations()

			// Select top 8 recommendations (padding if fewer than 8 are available)
			n := 8
			if len(schemaRecs) > n {
				schemaRecs = schemaRecs[:n]
			}

			return schemaRecs
		},
		"Always use top 8 SchemaTree recommendations",
	)

	return &wf
}
