import argparse
import sys
import json
from pathlib import Path
from pick import pick


def run_fetch_command(source: str):
    """Run the fetch command for the specified source."""
    if source.lower() == "slp3":
        from src.fetch_data.fetch_jurafsky_slp3 import fetch_all_slp3_content

        fetch_all_slp3_content()


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
    from src.anki.deck_creation import create_anki_deck
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
    parser = argparse.ArgumentParser(
        description="Anki flashcard generator for Jurafsky & Martin SLP3"
    )
    parser.add_argument(
        "--fetch", "-f", action="store_true", help="Fetch content from specified source"
    )
    parser.add_argument(
        "--source",
        "-s",
        type=str,
        choices=["slp3"],
        help="Source to fetch content from",
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
    elif args.create_cards:
        run_create_cards_command()
    elif args.make_deck:
        if not args.chapter:
            print("❌ --chapter is required when using --make-deck")
            sys.exit(1)
        run_make_deck_command(args.chapter)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
