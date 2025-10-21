import argparse
import sys
import json
import asyncio
from pathlib import Path
from pick import pick


def run_fetch_command(source: str):
    """Run the fetch command for the specified source."""
    if source.lower() == "slp3":
        from src.fetch_data.fetch_jurafsky_slp3 import fetch_all_slp3_content

        fetch_all_slp3_content()
    elif source.lower() == "neetcode":
        asyncio.run(fetch_neetcode_problems())
    else:
        print(f"❌ Unknown source: {source}")
        sys.exit(1)


async def fetch_neetcode_problems():
    """Fetch NeetCode 150 problems from LeetCode."""
    from src.fetch_data.fetch_leetcode import LeetcodeData
    
    print("🚀 Fetching NeetCode 150 problems...")
    
    # NeetCode 150 list ID
    neetcode_list_id = "plakya4j"
    
    # Initialize LeetCode data fetcher for all problems in the list
    leetcode_data = LeetcodeData(
        start=0,
        stop=2**64,  # Get all problems
        page_size=500,
        list_id=neetcode_list_id
    )
    
    # Get all problem handles (slugs)
    problem_handles = await leetcode_data.all_problems_handles()
    print(f"📊 Found {len(problem_handles)} problems in NeetCode 150")
    
    # Create output directory
    output_dir = Path("data/neetcode")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save problem data
    problems_data = []
    for handle in problem_handles:
        problem_data = {
            "slug": handle,
            "title": await leetcode_data.title(handle),
            "problem_id": await leetcode_data.problem_id(handle),
            "description": await leetcode_data.description(handle),
            "difficulty": await leetcode_data.difficulty(handle),
            "category": await leetcode_data.category(handle),
            "tags": await leetcode_data.tags(handle)
        }
        problems_data.append(problem_data)
    
    # Save to JSON file
    output_file = output_dir / "neetcode_problems.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(problems_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(problems_data)} problems to {output_file}")


def run_process_leetcode_command(source: str):
    """Process LeetCode problems and generate cards using LLM."""
    if source.lower() == "neetcode":
        print("🚀 Starting NeetCode 150 processing...")
        
        # Import and run the neetcode pipeline
        import neetcode_pipeline
        neetcode_pipeline.main()
        
        print("✅ NeetCode processing completed!")
    else:
        print(f"❌ LeetCode processing not implemented for source: {source}")
        sys.exit(1)


def run_make_slp3_deck_command(chapter_num: int):
    """Create Anki deck from SLP3 cards."""
    from src.anki.slp3_deck_creation import create_anki_deck
    from src.models.cards import QACard, ClozeCard, EnumerationCard

    # Check if cards file exists
    cards_file = Path(f"data/slp3/cards/chapter_{chapter_num}/atomic_cards.json")
    if not cards_file.exists():
        print(f"❌ Cards file not found: {cards_file}")
        print(f"Please run --create-cards first to generate cards for chapter {chapter_num}")
        sys.exit(1)

    print(f"📖 Loading cards for Chapter {chapter_num}...")

    # Load cards from JSON
    with open(cards_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cards_data = data.get("cards", [])
    if not cards_data:
        print(f"❌ No cards found in {cards_file}")
        sys.exit(1)

    # Convert JSON data back to CardType objects
    cards = []
    for card_data in cards_data:
        card_type = card_data.get("type")
        if card_type == "Q&A":
            cards.append(QACard(**card_data))
        elif card_type == "Cloze":
            cards.append(ClozeCard(**card_data))
        elif card_type == "Enumeration":
            cards.append(EnumerationCard(**card_data))

    print(f"✅ Loaded {len(cards)} cards")

    # Create Anki deck
    deck_name = f"{chapter_num:02d} chapter slp3"
    output_filename = f"data/slp3/anki_decks/chapter_{chapter_num}.apkg"

    create_anki_deck(cards, deck_name, output_filename)


def run_make_neetcode_deck_command():
    """Create Anki deck from NeetCode cards."""
    print("🎴 Creating NeetCode 150 Anki deck...")
    
    # Import and run the deck creation
    from src.anki.leetcode_deck_creation import main as create_deck_main
    create_deck_main()
    
    print("✅ NeetCode deck creation completed!")


def run_make_deck_command(source: str, chapter_num: int = None):
    """Create Anki deck from existing cards."""
    if source.lower() == "slp3":
        if not chapter_num:
            print("❌ --chapter is required when creating SLP3 deck")
            sys.exit(1)
        run_make_slp3_deck_command(chapter_num)
    elif source.lower() == "neetcode":
        run_make_neetcode_deck_command()
    else:
        print(f"❌ Deck creation not implemented for source: {source}")
        sys.exit(1)


def run_create_cards_command():
    """Interactive chapter selection and card creation."""
    from slp3_pipeline import create_cards_for_chapters

    # Check if data directory exists
    data_dir = Path("data/slp3/txt")
    if not data_dir.exists():
        print(
            "❌ Chapter text files not found. Please run --fetch --source slp3 first."
        )
        sys.exit(1)

    # Find available chapters
    available_chapters = []
    for chapter_file in sorted(data_dir.glob("chapter_*.txt")):
        chapter_num = int(chapter_file.stem.split("_")[1])
        available_chapters.append(chapter_num)

    if not available_chapters:
        print("❌ No chapter files found in data/slp3/txt/")
        sys.exit(1)

    print(f"Found {len(available_chapters)} chapters: {sorted(available_chapters)}")

    # Create simple chapter options
    chapter_options = [f"Chapter {ch}" for ch in sorted(available_chapters)]

    print("\n🎯 Select chapters to process for atomic card generation:")
    print("Use SPACE to select, ENTER to confirm")

    try:
        selected_options = pick(
            chapter_options,
            "Select chapters (multi-select with SPACE):",
            multiselect=True,
            min_selection_count=1,
        )
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Operation cancelled.")
        sys.exit(0)

    # Parse selections - multiselect returns list of (option_text, index) tuples
    selected_chapters = []
    for option_text, index in selected_options:
        # Parse "Chapter 8" -> 8
        chapter_num = int(option_text.split()[1])
        selected_chapters.append(chapter_num)

    selected_chapters = sorted(selected_chapters)
    print(f"\n✅ Selected chapters: {selected_chapters}")

    # Process selected chapters
    create_cards_for_chapters(selected_chapters)


def run_make_deck_command(chapter_num: int):
    """Load cards for a chapter and create an Anki deck."""
    from src.anki.slp3_deck_creation import create_anki_deck
    from src.models.cards import QACard, ClozeCard, EnumerationCard

    # Check if cards file exists
    cards_file = Path(f"data/slp3/cards/chapter_{chapter_num}/atomic_cards.json")
    if not cards_file.exists():
        print(f"❌ Cards file not found: {cards_file}")
        print(
            f"Please run --create-cards first to generate cards for chapter {chapter_num}"
        )
        sys.exit(1)

    print(f"📖 Loading cards for Chapter {chapter_num}...")

    # Load cards from JSON
    with open(cards_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cards_data = data.get("cards", [])
    if not cards_data:
        print(f"❌ No cards found in {cards_file}")
        sys.exit(1)

    # Convert JSON data back to CardType objects
    cards = []
    for card_data in cards_data:
        card_type = card_data.get("type")
        if card_type == "Q&A":
            cards.append(QACard(**card_data))
        elif card_type == "Cloze":
            cards.append(ClozeCard(**card_data))
        elif card_type == "Enumeration":
            cards.append(EnumerationCard(**card_data))

    print(f"✅ Loaded {len(cards)} cards")

    # Create Anki deck
    deck_name = f"{chapter_num:02d} chapter slp3"
    output_filename = f"data/slp3/anki_decks/chapter_{chapter_num}.apkg"

    create_anki_deck(cards, deck_name, output_filename)


def create_parser():
    """Create and configure the argument parser."""
    epilog = """
examples:
  SLP3:
  python main.py -f -s slp3          # Fetch
  python main.py -c                  # Create cards (interactive)
  python main.py -m -s slp3 -ch 8    # Make deck

  NeetCode:
  python main.py -f -s neetcode      # Fetch
  python main.py -pl -s neetcode     # Process with LLM
  python main.py -m -s neetcode      # Make deck
"""
    
    parser = argparse.ArgumentParser(
        description="Anki flashcard generator for Jurafsky & Martin SLP3 and LeetCode problems",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--fetch", "-f", action="store_true", help="Fetch content from specified source"
    )
    parser.add_argument(
        "--source",
        "-s",
        type=str,
        choices=["slp3", "neetcode"],
        help="Source to fetch content from",
    )
    parser.add_argument(
        "--process-leetcode",
        "-pl",
        action="store_true",
        help="Process LeetCode problems and generate cards using LLM",
    )
    parser.add_argument(
        "--create-cards",
        "-c",
        action="store_true",
        help="Interactive chapter selection for card generation",
    )
    parser.add_argument(
        "--make-deck",
        "-m",
        action="store_true",
        help="Create Anki deck from existing cards",
    )
    parser.add_argument(
        "--chapter", "-ch", type=int, help="Chapter number for deck creation"
    )
    return parser


def main():
    """Main entry point with argument parsing."""
    parser = create_parser()
    args = parser.parse_args()

    if args.fetch:
        if not args.source:
            print("❌ --source is required when using --fetch")
            sys.exit(1)
        run_fetch_command(args.source)
    elif args.process_leetcode:
        if not args.source:
            print("❌ --source is required when using --process-leetcode")
            sys.exit(1)
        run_process_leetcode_command(args.source)
    elif args.create_cards:
        run_create_cards_command()
    elif args.make_deck:
        if not args.source:
            print("❌ --source is required when using --make-deck")
            sys.exit(1)
        run_make_deck_command(args.source, args.chapter)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
