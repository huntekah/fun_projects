#!/usr/bin/env python3
"""
Mock LeetCode Pipeline

Test script to process specific LeetCode problems and generate cards.
Filters for problems with IDs 329 and 10, processes them through the
card creation pipeline, and saves the results.
"""

import json
from pathlib import Path
from typing import List

from src.models.leetcode_cards import FetchedLeetcodeProblem, LeetcodeCard
from src.processing.leetcode_card_creation import load_and_validate_problems, process_leetcode_problems


def filter_problems_by_ids(problems: List[FetchedLeetcodeProblem], target_ids: List[str]) -> List[FetchedLeetcodeProblem]:
    """Filter problems by their problem IDs."""
    filtered = []
    for problem in problems:
        if problem.problem_id in target_ids:
            filtered.append(problem)
            print(f"✅ Found problem {problem.problem_id}: {problem.title}")
    
    print(f"📊 Filtered {len(filtered)} problems from {len(problems)} total")
    return filtered


def save_cards_to_json(cards: List[LeetcodeCard], output_path: str):
    """Save LeetcodeCard objects to JSON file."""
    cards_data = [card.model_dump() for card in cards]
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cards_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(cards_data)} cards to {output_path}")


def main():
    """Main pipeline execution."""
    print("🚀 Starting mock LeetCode pipeline...")
    
    # Target problem IDs to process
    target_problem_ids = ["329", "10"]
    
    # Input and output paths
    input_file = "data/neetcode/neetcode_problems.json"
    output_file = "data/neetcode/llm_problem_solutions.json"
    
    try:
        # Load and validate problems from JSON
        print(f"📂 Loading problems from {input_file}")
        all_problems: List[FetchedLeetcodeProblem] = load_and_validate_problems(input_file)
        
        # Filter for target problems
        print(f"🔍 Filtering for problems with IDs: {target_problem_ids}")
        target_problems = filter_problems_by_ids(all_problems, target_problem_ids)
        
        if not target_problems:
            print("❌ No target problems found! Check if the problem IDs exist in the dataset.")
            return
        
        # Generate cards using LLM
        print("🤖 Generating LeetCode cards using LLM...")
        cards_dict = process_leetcode_problems(target_problems)
        
        # Convert to list for JSON serialization
        cards_list: List[LeetcodeCard] = list(cards_dict.values())
        
        if not cards_list:
            print("❌ No cards were generated successfully!")
            return
        
        # Save results
        save_cards_to_json(cards_list, output_file)
        
        print(f"✅ Pipeline completed successfully!")
        print(f"📊 Generated {len(cards_list)} cards for {len(target_problems)} problems")
        
        # Show summary
        for i, card in enumerate(cards_list, 1):
            num_solutions = len(card.solutions)
            print(f"   {i}. {card.problem_description[:60]}... ({num_solutions} solution{'s' if num_solutions != 1 else ''})")
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("💡 Make sure to run 'python main.py -f -s neetcode' first to fetch the problems")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()