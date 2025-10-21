#!/usr/bin/env python3
"""
NeetCode 150 Pipeline

Process the full NeetCode 150 problem set and generate Anki flashcards.
Filters for the complete list of 150 problems, processes them through the
card creation pipeline, and saves the results.
"""

import json
from pathlib import Path
from typing import List

from src.models.leetcode_cards import FetchedLeetcodeProblem, LeetcodeCard, AnkiLeetcodeCard, create_leetcode_anki_cards
from src.processing.leetcode_card_creation import load_and_validate_problems, process_leetcode_problems


# NeetCode 150 problem IDs
NEETCODE_150_IDS = [
    "1", "2", "3", "4", "5", "518", "7", "1448", "10", "11", "994", "15", "17", "19", "20", "21", "22", "23", "25", "543", 
    "33", "36", "39", "40", "42", "43", "45", "46", "48", "49", "50", "51", "53", "54", "55", "56", "57", "567", "572", "62", 
    "66", "70", "72", "73", "74", "76", "78", "79", "84", "90", "91", "2013", "97", "98", "100", "102", "1046", "104", "105", 
    "621", "110", "115", "121", "124", "125", "127", "128", "130", "131", "133", "134", "647", "136", "138", "139", "141", 
    "143", "146", "150", "152", "153", "155", "678", "167", "1584", "684", "695", "190", "191", "198", "199", "200", "202", 
    "206", "207", "208", "210", "211", "212", "213", "215", "217", "226", "739", "1143", "230", "743", "235", "746", "238", 
    "239", "242", "252", "253", "763", "261", "268", "269", "271", "703", "704", "778", "286", "287", "787", "295", "297", 
    "300", "309", "312", "322", "323", "329", "332", "338", "347", "355", "846", "371", "853", "875", "416", "417", "424", 
    "435", "1851", "1899", "494", "973", "981"
]


def filter_problems_by_ids(problems: List[FetchedLeetcodeProblem], target_ids: List[str]) -> List[FetchedLeetcodeProblem]:
    """Filter problems by their problem IDs."""
    filtered = []
    found_ids = set()
    
    for problem in problems:
        if problem.problem_id in target_ids:
            filtered.append(problem)
            found_ids.add(problem.problem_id)
            print(f"✅ Found problem {problem.problem_id}: {problem.title}")
    
    missing_ids = set(target_ids) - found_ids
    if missing_ids:
        print(f"⚠️  Missing problems: {sorted(missing_ids, key=int)}")
    
    print(f"📊 Filtered {len(filtered)} problems from {len(problems)} total")
    return filtered


def save_cards_to_json(cards: List[LeetcodeCard], output_path: str):
    """Save LeetcodeCard objects to JSON file."""
    cards_data = [card.model_dump() for card in cards]
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cards_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(cards_data)} LeetcodeCard objects to {output_path}")


def save_anki_cards_to_json(anki_cards: List[AnkiLeetcodeCard], output_path: str):
    """Save AnkiLeetcodeCard objects to JSON file."""
    cards_data = [card.model_dump() for card in anki_cards]
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cards_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(cards_data)} AnkiLeetcodeCard objects to {output_path}")


def main():
    """Main pipeline execution."""
    print("🚀 Starting NeetCode 150 pipeline...")
    
    # Input and output paths
    input_file = "data/neetcode/neetcode_problems.json"
    llm_output_file = "data/neetcode/neetcode_150_llm_solutions.json"
    anki_output_file = "data/neetcode/neetcode_150_anki_cards.json"
    
    try:
        # Load and validate problems from JSON
        print(f"📂 Loading problems from {input_file}")
        all_problems = load_and_validate_problems(input_file)
        
        # Filter for NeetCode 150 problems
        print(f"🔍 Filtering for NeetCode 150 problems ({len(NEETCODE_150_IDS)} total)")
        target_problems = filter_problems_by_ids(all_problems, NEETCODE_150_IDS)
        
        if not target_problems:
            print("❌ No target problems found! Check if the problem IDs exist in the dataset.")
            return
        
        # Generate cards using LLM
        print("🤖 Generating LeetCode cards using LLM...")
        cards_dict = process_leetcode_problems(target_problems)
        
        # Convert to list for processing
        cards_list = list(cards_dict.values())
        
        if not cards_list:
            print("❌ No cards were generated successfully!")
            return
        
        # Save LLM-generated cards
        save_cards_to_json(cards_list, llm_output_file)
        
        # Create Anki-ready cards
        print("🎴 Creating Anki-ready cards...")
        all_anki_cards = []
        
        # Match problems with their generated cards
        for problem in target_problems:
            if problem.slug in cards_dict:
                leetcode_card = cards_dict[problem.slug]
                anki_cards: List[AnkiLeetcodeCard] = create_leetcode_anki_cards(problem, leetcode_card)
                all_anki_cards.extend(anki_cards)
                print(f"✅ Created {len(anki_cards)} Anki cards for: {problem.title}")
            else:
                print(f"⚠️  No LLM card found for: {problem.title}")
        
        if not all_anki_cards:
            print("❌ No Anki cards were created!")
            return
        
        # Save Anki-ready cards
        save_anki_cards_to_json(all_anki_cards, anki_output_file)
        
        print(f"✅ Pipeline completed successfully!")
        print(f"📊 Processed {len(target_problems)} problems")
        print(f"📊 Generated {len(cards_list)} LeetCode cards")
        print(f"📊 Created {len(all_anki_cards)} Anki-ready cards")
        
        # Show summary by solution type
        solution_types = {}
        for card in all_anki_cards:
            solution_types[card.solution_type] = solution_types.get(card.solution_type, 0) + 1
        
        print(f"🎯 Solution breakdown:")
        for sol_type, count in sorted(solution_types.items()):
            print(f"   {sol_type}: {count} cards")
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("💡 Make sure to run 'python main.py -f -s neetcode' first to fetch the problems")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()