"""
SLP3 Pipeline - End-to-end processing of textbook chapters into atomic flashcards.
"""

import json
from pathlib import Path
from typing import List
from src.processing.splitter import split_to_chunks
from src.processing.preprocessor import clean_chapter_text
from src.processing.merger import merge_chunks
from src.processing.semantic_chunker import split_markdown_into_sections
from src.processing.atomic_chunker import extract_atomic_cards, fix_content, fix_formatting
from src.models.cards import CardType, ClozeCard, EnumerationCard, QACard
from tqdm import tqdm
import traceback


def chapter_pipeline(
    raw_chapter_text: str,
    chapter_name: str,
    window_size: int = 6000,
    overlap: int = 3000,
    data_dir: Path | None = None,
    skip_if_cleaned: bool = False,
) -> List[CardType]:
    """
    Process a raw chapter text through the complete pipeline to generate atomic flashcards.

    Args:
        raw_chapter_text: Raw text extracted from PDF
        chapter_name: Name of the chapter (e.g., "chapter_8")
        window_size: Size of chunks for processing (default: 6000)
        overlap: Overlap between chunks (default: 3000)
        data_dir: Base data directory (defaults to ./data/slp3)
        skip_if_cleaned: If True, skip cleaning steps (1-3) and use existing cleaned text

    Returns:
        List of atomic flashcards extracted from all sections of the chapter
    """
    
    if data_dir is None:
        data_dir = Path("data/slp3")

    # Check if we should skip cleaning steps and use existing cleaned text
    cleaned_txt_dir = data_dir / "cleaned_txt"
    cleaned_file = cleaned_txt_dir / f"{chapter_name}.txt"
    
    if skip_if_cleaned and cleaned_file.exists():
        print(f"📄 Using existing cleaned text: {cleaned_file}")
        with open(cleaned_file, "r", encoding="utf-8") as f:
            merged_text = f.read()
    else:
        # Step 1: Split into overlapping chunks
        chunks = list(split_to_chunks(raw_chapter_text, window_size, overlap))

        # Step 2: Clean chunks with LLM
        cleaned_chunks = []
        for chunk in tqdm(chunks, desc=f"Cleaning chunks of {chapter_name}"):
            cleaned_chunk = clean_chapter_text(chapter_name, chunk)
            cleaned_chunks.append(cleaned_chunk)

        # Step 3: Merge cleaned chunks
        merged_text = merge_chunks(cleaned_chunks, overlap)
        
        # Save cleaned text
        cleaned_txt_dir.mkdir(parents=True, exist_ok=True)
        
        with open(cleaned_file, "w", encoding="utf-8") as f:
            f.write(merged_text)
        
        print(f"💾 Saved cleaned text to: {cleaned_file}")

    # Step 4: Split into semantic sections
    sections = split_markdown_into_sections(merged_text)

    # Step 5: Extract atomic cards from each section
    all_cards = []

    for section in tqdm(sections, desc=f"Extracting cards from {chapter_name}"):
        heading = section["heading"]
        content = section.get("content", "")

        # Skip very short sections
        if len(content.strip()) < 50:
            continue

        # Extract cards from this section
        try:
            section_text = f"# {heading}\n\n{content}"
            cards = extract_atomic_cards(section_text)
            card_info = [(section_text, card) for card in cards]
            all_cards.extend(card_info)
        except Exception as e:
            # Log error but continue processing other sections
            print(f"Warning: Failed to extract cards from section '{heading}': {e}")
            continue

    intermediate_cards_dir = data_dir / "tmp_fix_cards_step"
    intermediate_cards_dir.mkdir(parents=True, exist_ok=True)
    
    raw_cards = []
    content_fixed_cards = []
    final_cards = []
    new_cards = []
    
    for section_text, card in tqdm(all_cards, desc="Fixing extracted cards", smoothing=0.1):
        raw_cards.append(json.dumps(card.model_dump(), indent=2, ensure_ascii=False))
        
        fixed_content_card: QACard | ClozeCard | EnumerationCard = fix_content(section_text, card)
        content_fixed_cards.append(json.dumps(fixed_content_card.model_dump(), indent=2, ensure_ascii=False))
        
        fixed_card: QACard | ClozeCard | EnumerationCard = fix_formatting(fixed_content_card)
        final_cards.append(json.dumps(fixed_card.model_dump(), indent=2, ensure_ascii=False))
        
        new_cards.append(fixed_card)
    
    with open(intermediate_cards_dir / f"{chapter_name}_01_raw.json", "w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(raw_cards) + "\n]")
    
    with open(intermediate_cards_dir / f"{chapter_name}_02_fixed_content_card.json", "w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(content_fixed_cards) + "\n]")
        
    with open(intermediate_cards_dir / f"{chapter_name}_03_fixed_card.json", "w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(final_cards) + "\n]")

    all_cards = new_cards

    return all_cards


def create_cards_for_chapters(
    chapter_numbers: List[int], 
    data_dir: Path | None = None,
    skip_if_cleaned: bool = False,
) -> None:
    """
    Create atomic cards for selected chapters and save them to organized directories.

    Args:
        chapter_numbers: List of chapter numbers to process (e.g., [2, 8, 15])
        data_dir: Base data directory (defaults to ./data/slp3)
        skip_if_cleaned: If True, skip expensive cleaning steps and use existing cleaned text
    """
    if data_dir is None:
        data_dir = Path("data/slp3")

    txt_dir = data_dir / "txt"
    cards_dir = data_dir / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)

    for chapter_num in chapter_numbers:
        print(f"\n{'='*60}")
        print(f"Processing Chapter {chapter_num}")
        print(f"{'='*60}")

        # Load chapter text
        chapter_file = txt_dir / f"chapter_{chapter_num}.txt"
        if not chapter_file.exists():
            print(f"❌ Chapter {chapter_num} file not found: {chapter_file}")
            continue

        print(f"📖 Loading chapter {chapter_num}...")
        with open(chapter_file, "r", encoding="utf-8") as f:
            raw_text = f.read()

        print(f"📊 Chapter size: {len(raw_text):,} characters")

        # Process through pipeline
        try:
            print(f"⚙️ Running pipeline... {skip_if_cleaned=}")
            cards = chapter_pipeline(raw_text, f"chapter_{chapter_num}", data_dir=data_dir, skip_if_cleaned=skip_if_cleaned)

            if not cards:
                print(f"⚠️ No cards generated for chapter {chapter_num}")
                continue

            print(f"🎯 Generated {len(cards)} atomic cards")

            # Count by type
            card_counts = {"Q&A": 0, "Cloze": 0, "Enumeration": 0}
            for card in cards:
                card_counts[card.type] += 1

            print(
                f"📋 Card types: Q&A={card_counts['Q&A']}, Cloze={card_counts['Cloze']}, Enum={card_counts['Enumeration']}"
            )

            # Create chapter directory
            chapter_cards_dir = cards_dir / f"chapter_{chapter_num}"
            chapter_cards_dir.mkdir(exist_ok=True)

            # Save cards as JSON
            cards_data = []
            for card in cards:
                card_dict = card.model_dump()
                cards_data.append(card_dict)

            output_file = chapter_cards_dir / "atomic_cards.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "chapter": chapter_num,
                        "total_cards": len(cards),
                        "card_counts": card_counts,
                        "cards": cards_data,
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            print(f"💾 Saved to: {output_file}")
            print(f"✅ Chapter {chapter_num} completed successfully!")

        except Exception as e:
            traceback.print_exc()
            print(f"❌ Error processing chapter {chapter_num}: {e}")
            continue

    print(f"\n🎉 Batch processing completed for chapters: {chapter_numbers}")
