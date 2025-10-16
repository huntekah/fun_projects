import argparse
import sys
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
        print("❌ Chapter text files not found. Please run --fetch --source slp3 first.")
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
            min_selection_count=1
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


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(description="Anki flashcard generator for Jurafsky & Martin SLP3")
    parser.add_argument("--fetch", action="store_true", help="Fetch content from specified source")
    parser.add_argument("--source", type=str, choices=["slp3"], help="Source to fetch content from")
    parser.add_argument("--create-cards", "-c", action="store_true", help="Interactive chapter selection for card generation")
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
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
