import argparse
import sys


def run_fetch_command(source: str):
    """Run the fetch command for the specified source."""
    if source.lower() == "slp3":
        from src.fetch_data.fetch_jurafsky_slp3 import fetch_all_slp3_content
        fetch_all_slp3_content()


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(description="Anki flashcard generator for Jurafsky & Martin SLP3")
    parser.add_argument("--fetch", action="store_true", help="Fetch content from specified source")
    parser.add_argument("--source", type=str, choices=["slp3"], help="Source to fetch content from")
    return parser


def main():
    """Main entry point with argument parsing."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.fetch:
        if not args.source:
            sys.exit(1)
        run_fetch_command(args.source)


if __name__ == "__main__":
    main()
