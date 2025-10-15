"""
Test script for text cleaning functionality.
Tests the preprocessor on Chapter 2 text file.
"""

import logging
from pathlib import Path
from src.processing.preprocessor import clean_chapter_text
from dotenv import load_dotenv


load_dotenv()
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_chapter_2_cleaning():
    """Test text cleaning on Chapter 2."""
    
    print("=" * 60)
    print("Testing Text Cleaning on Chapter 2")
    print("=" * 60)
    
    try:
        # Load raw chapter 2 text
        project_root = Path(__file__).parent
        chapter_2_file = project_root / "data" / "slp3" / "txt" / "chapter_2.txt"
        
        if not chapter_2_file.exists():
            print(f"❌ Chapter 2 file not found: {chapter_2_file}")
            return False
        
        with open(chapter_2_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        
        print(f"📖 Loaded Chapter 2: {len(raw_text)} characters")
        print(f"📝 Preview of raw text:")
        print("-" * 40)
        print(raw_text[:500] + "...")
        print("-" * 40)
        
        # Clean the text using our function
        print("\n🧹 Starting text cleaning with Gemini...")
        cleaned_text = clean_chapter_text("chapter_2", raw_text[:5000])
        
        print(f"✅ Cleaning completed!")
        print(f"📊 Results:")
        print(f"   - Original length: {len(raw_text)} characters")
        print(f"   - Cleaned length: {len(cleaned_text)} characters")
        print(f"   - Change: {len(cleaned_text) - len(raw_text):+d} characters")
        
        print(f"\n📝 Preview of cleaned text:")
        print("-" * 40)
        print(cleaned_text[:500] + "...")
        print("-" * 40)
        
        # Save the cleaned text for inspection
        output_file = project_root / "data" / "slp3" / "chapter_2_test_cleaned.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        print(f"\n💾 Saved cleaned text to: {output_file}")
        print("✅ Test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.exception("Full error details:")
        return False




if __name__ == "__main__":

    success1 = test_chapter_2_cleaning()
    