"""
Test script for text cleaning pipeline.
Tests the complete chunked cleaning pipeline on Chapter 2.
"""

from pathlib import Path
from src.processing.preprocessor import clean_chapter_text
from src.processing.splitter import split_to_chunks
from src.processing.merger import merge_chunks
from src.processing.semantic_chunker import split_markdown_into_sections, sanitize_filename
from src.processing.atomic_chunker import extract_atomic_cards
from dotenv import load_dotenv

load_dotenv()

WINDOW_SIZE = 6000
OVERLAP = 3000


def test_chunked_cleaning_pipeline():
    """Test the complete chunked cleaning pipeline on Chapter 8."""
    
    print("=" * 60)
    print("Testing Chunked Cleaning Pipeline on Chapter 8")
    print("=" * 60)
    
    try:
        project_root = Path(__file__).parent
        chapter_8_file = project_root / "data" / "slp3" / "txt" / "chapter_8.txt"
        
        if not chapter_8_file.exists():
            print(f"❌ Chapter 8 file not found: {chapter_8_file}")
            return False
        
        with open(chapter_8_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        
        print(f"📖 Loaded Chapter 8: {len(raw_text)} characters")
        print(f"⚙️ Pipeline config: window={WINDOW_SIZE}, overlap={OVERLAP}")
        
        print("\n📄 Step 1: Splitting into chunks...")
        chunks = list(split_to_chunks(raw_text, WINDOW_SIZE, OVERLAP))
        print(f"   Created {len(chunks)} chunks")
        
        print("\n🧹 Step 2: Cleaning chunks with LLM...")
        cleaned_chunks = []
        for i, chunk in enumerate(chunks):
            cleaned_chunk = clean_chapter_text("chapter_8", chunk)
            print(f"   Cleaning chunk {i+1}/{len(chunks)} ({len(chunk)} chars)... -> {len(cleaned_chunk)} chars")
            cleaned_chunks.append(cleaned_chunk)
        
        with open(project_root / "data" / "slp3" / "chapter_8_cleaned_chunks.txt", 'w', encoding='utf-8') as f:
            for i, c in enumerate(cleaned_chunks):
                f.write(f"--- Chunk {i+1} ---\n")
                f.write(c + "\n\n")
        
        print("\n🔗 Step 3: Merging cleaned chunks...")
        merged_text = merge_chunks(cleaned_chunks, OVERLAP)
        
        print(f"✅ Pipeline completed!")
        print(f"📊 Results:")
        print(f"   - Original length: {len(raw_text)} characters")
        print(f"   - Final length: {len(merged_text)} characters")
        print(f"   - Change: {len(merged_text) - len(raw_text):+d} characters")
        print(f"   - Processed {len(chunks)} chunks")
        
        output_file = project_root / "data" / "slp3" / "chapter_8_pipeline_cleaned.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(merged_text)
        
        print(f"\n💾 Saved final result to: {output_file}")
        
        print("\n📚 Step 4: Semantic chunking...")
        sections = split_markdown_into_sections(merged_text)
        print(f"   Found {len(sections)} semantic sections")
        
        # Save each section to semantic_chunks directory
        semantic_chunks_dir = project_root / "data" / "slp3" / "chapter_8_semantic_chunks"
        semantic_chunks_dir.mkdir(parents=True, exist_ok=True)
        
        for i, section in enumerate(sections):
            heading = section['heading']
            content = section.get('content', '')
            level = section['level']
            
            filename = f"{i:02d}_{sanitize_filename(heading)}.txt"
            section_file = semantic_chunks_dir / filename
            
            with open(section_file, 'w', encoding='utf-8') as f:
                f.write(f"# {heading}\n\n")
                f.write(content)
            
            print(f"   Saved section: {filename} (Level {level}, {len(content)} chars)")
        
        # Step 5: Atomic card extraction
        print("\n🎯 Step 5: Atomic card extraction...")
        atomic_results_dir = project_root / "data" / "slp3" / "chapter_8_atomic_results"
        atomic_results_dir.mkdir(parents=True, exist_ok=True)
        
        total_cards = 0
        
        for i, section in enumerate(sections):
            heading = section['heading']
            content = section.get('content', '')
            
            if len(content.strip()) < 50:  # Skip very short sections
                print(f"   Skipping short section: {heading}")
                continue
                
            print(f"   Processing section {i+1}/{len(sections)}: {heading[:30]}...")
            
            try:
                # Extract atomic cards from this section
                section_text = f"# {heading}\n\n{content}"
                cards = extract_atomic_cards(section_text)
                
                if cards:
                    print(f"     → Extracted {len(cards)} cards")
                    
                    # Count by type
                    card_counts = {"Q&A": 0, "Cloze": 0, "Enumeration": 0}
                    for card in cards:
                        card_counts[card.type] += 1
                    
                    print(f"     → Types: Q&A={card_counts['Q&A']}, Cloze={card_counts['Cloze']}, Enum={card_counts['Enumeration']}")
                    
                    # Save cards for this section
                    filename = f"{i:02d}_{sanitize_filename(heading)}_cards.json"
                    result_file = atomic_results_dir / filename
                    
                    # Convert cards to dict for JSON serialization
                    cards_data = []
                    for card in cards:
                        card_dict = card.model_dump()
                        cards_data.append(card_dict)
                    
                    import json
                    with open(result_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "source_section": heading,
                            "section_content_length": len(content),
                            "total_cards": len(cards),
                            "card_counts": card_counts,
                            "cards": cards_data
                        }, f, indent=2, ensure_ascii=False)
                    
                    total_cards += len(cards)
                else:
                    print(f"     → No cards extracted (filtered out)")
                    
            except Exception as e:
                print(f"     ❌ Error processing section '{heading}': {e}")
                continue
        
        print(f"\n✅ Full pipeline test completed successfully!")
        print(f"📊 Total atomic cards extracted: {total_cards}")
        print(f"💾 Semantic sections saved to: {semantic_chunks_dir}")
        print(f"💾 Atomic cards saved to: {atomic_results_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed with error: {e}")
        return False


if __name__ == "__main__":
    test_chunked_cleaning_pipeline()
    