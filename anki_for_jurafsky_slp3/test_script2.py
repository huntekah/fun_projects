"""
Test script for atomic knowledge extraction.
Tests the atomic chunker on specific semantic chunks.
"""

from pathlib import Path
from src.processing.atomic_chunker import extract_atomic_cards
from src.models.cards import QACard, ClozeCard, EnumerationCard
from dotenv import load_dotenv
import json

load_dotenv()

# Test chunks to process
TEST_CHUNKS = [
    "47_210_Summary.txt",
    "52_23_Implement_an_ELIZ.txt",
    "53_24_Compute_the_edit_.txt",
    "15_243_BPE_in_practice.txt",
    "57_Exercises.txt",
]


def test_atomic_extraction():
    """Test atomic knowledge extraction on selected chunks."""

    print("=" * 60)
    print("Testing Atomic Knowledge Extraction")
    print("=" * 60)

    project_root = Path(__file__).parent
    semantic_chunks_dir = project_root / "data" / "slp3" / "semantic_chunks"
    results_dir = project_root / "data" / "slp3" / "atomic_results"
    results_dir.mkdir(parents=True, exist_ok=True)

    total_cards = 0

    for chunk_file in TEST_CHUNKS:
        chunk_path = semantic_chunks_dir / chunk_file

        if not chunk_path.exists():
            print(f"❌ Chunk not found: {chunk_file}")
            continue

        print(f"\n📄 Processing: {chunk_file}")

        # Read the chunk content
        with open(chunk_path, "r", encoding="utf-8") as f:
            chunk_content = f.read()

        print(f"   📊 Chunk size: {len(chunk_content)} characters")

        try:
            # Extract atomic cards
            cards = extract_atomic_cards(chunk_content)
            print(f"   🎯 Extracted {len(cards)} atomic cards")

            # Count by type
            card_counts = {"Q&A": 0, "Cloze": 0, "Enumeration": 0}
            for card in cards:
                card_counts[card.type] += 1

            print(
                f"   📋 Card types: Q&A={card_counts['Q&A']}, Cloze={card_counts['Cloze']}, Enum={card_counts['Enumeration']}"
            )

            # Save results
            result_file = results_dir / f"{chunk_file.replace('.txt', '_cards.json')}"

            # Convert cards to dict for JSON serialization
            cards_data = []
            for card in cards:
                card_dict = card.model_dump()
                cards_data.append(card_dict)

            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "source_chunk": chunk_file,
                        "chunk_size": len(chunk_content),
                        "total_cards": len(cards),
                        "card_counts": card_counts,
                        "cards": cards_data,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            print(f"   💾 Saved to: {result_file}")

            # Print first few cards as examples
            print("   📋 Sample cards:")
            for i, card in enumerate(cards[:3]):  # Show first 3 cards
                if isinstance(card, QACard):
                    print(f"      {i+1}. Q&A - Q: {card.q[:50]}...")
                elif isinstance(card, ClozeCard):
                    print(f"      {i+1}. Cloze - {card.text[:50]}...")
                elif isinstance(card, EnumerationCard):
                    print(
                        f"      {i+1}. Enum - {card.prompt[:50]}... ({len(card.items)} items)"
                    )

            total_cards += len(cards)

        except Exception as e:
            print(f"   ❌ Error processing {chunk_file}: {e}")
            continue

    print("\n✅ Atomic extraction test completed!")
    print(f"📊 Total cards extracted: {total_cards}")
    print(f"💾 Results saved to: {results_dir}")


if __name__ == "__main__":
    test_atomic_extraction()
