"""
Test script for text cleaning pipeline.
Tests the complete chunked cleaning pipeline on Chapter 2.
"""

from pathlib import Path
from src.processing.preprocessor import clean_chapter_text
from src.processing.splitter import split_to_chunks
from src.processing.merger import merge_chunks
from dotenv import load_dotenv

load_dotenv()

WINDOW_SIZE = 6000
OVERLAP = 2000


def test_chunked_cleaning_pipeline():
    """Test the complete chunked cleaning pipeline on Chapter 2."""
    
    print("=" * 60)
    print("Testing Chunked Cleaning Pipeline on Chapter 2")
    print("=" * 60)
    
    try:
        project_root = Path(__file__).parent
        chapter_2_file = project_root / "data" / "slp3" / "txt" / "chapter_2.txt"
        
        if not chapter_2_file.exists():
            print(f"❌ Chapter 2 file not found: {chapter_2_file}")
            return False
        
        with open(chapter_2_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()[:20000]
        
        print(f"📖 Loaded Chapter 2: {len(raw_text)} characters")
        print(f"⚙️ Pipeline config: window={WINDOW_SIZE}, overlap={OVERLAP}")
        
        print("\n📄 Step 1: Splitting into chunks...")
        chunks = list(split_to_chunks(raw_text, WINDOW_SIZE, OVERLAP))
        print(f"   Created {len(chunks)} chunks")
        
        print("\n🧹 Step 2: Cleaning chunks with LLM...")
        cleaned_chunks = []
        for i, chunk in enumerate(chunks):
            print(f"   Cleaning chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
            cleaned_chunk = clean_chapter_text("chapter_2", chunk)
            cleaned_chunks.append(cleaned_chunk)
        
        print("\n🔗 Step 3: Merging cleaned chunks...")
        merged_text = merge_chunks(cleaned_chunks, OVERLAP)
        
        print(f"✅ Pipeline completed!")
        print(f"📊 Results:")
        print(f"   - Original length: {len(raw_text)} characters")
        print(f"   - Final length: {len(merged_text)} characters")
        print(f"   - Change: {len(merged_text) - len(raw_text):+d} characters")
        print(f"   - Processed {len(chunks)} chunks")
        
        output_file = project_root / "data" / "slp3" / "chapter_2_pipeline_cleaned.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(merged_text)
        
        print(f"\n💾 Saved final result to: {output_file}")
        print("✅ Pipeline test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed with error: {e}")
        return False


if __name__ == "__main__":
    test_chunked_cleaning_pipeline()
    