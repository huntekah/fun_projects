import os
import requests
import fitz  # PyMuPDF
from tqdm import tqdm
from pathlib import Path

# Base configuration
BASE_URL = "https://web.stanford.edu/~jurafsky/slp3/"

# Get project root directory (where this script is relative to)
PROJECT_ROOT = Path(__file__).parent.parent.parent
PDF_DIR = PROJECT_ROOT / "data" / "slp3" / "pdf"
TEXT_DIR = PROJECT_ROOT / "data" / "slp3" / "txt"

# Ensure directories exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
TEXT_DIR.mkdir(parents=True, exist_ok=True)


def get_chapter_urls():
    """Generates the list of URLs for all chapters and appendices."""
    urls = {}
    # Chapters 2-28
    for i in range(2, 29):
        urls[f"chapter_{i}"] = f"{BASE_URL}{i}.pdf"
    # Appendices A-K
    for char_code in range(ord('A'), ord('L')):
        char = chr(char_code)
        urls[f"appendix_{char}"] = f"{BASE_URL}{char}.pdf"
    return urls


def download_and_extract_text(chapter_name, url):
    """Downloads a PDF and extracts its text if not already done."""
    pdf_path = PDF_DIR / f"{chapter_name}.pdf"
    text_path = TEXT_DIR / f"{chapter_name}.txt"

    # Check if text file already exists
    if text_path.exists():
        print(f"Text for {chapter_name} already exists. Skipping.")
        with open(text_path, 'r', encoding='utf-8') as f:
            return f.read()

    # Download PDF if it doesn't exist
    if not pdf_path.exists():
        print(f"Downloading {chapter_name}...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Downloaded {chapter_name}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to download {chapter_name}: {e}")
            return None
    
    # Extract text from PDF
    print(f"Extracting text from {chapter_name}...")
    full_text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                full_text += page.get_text()
                
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        print(f"✅ Extracted text from {chapter_name}")
        return full_text
        
    except Exception as e:
        print(f"❌ Failed to extract text from {chapter_name}: {e}")
        return None


def fetch_all_slp3_content():
    """
    Main function to fetch all SLP3 content.
    Downloads PDFs and extracts text for all chapters and appendices.
    
    Returns:
        dict: Dictionary mapping chapter names to their text content
    """
    print("🚀 Starting SLP3 content fetching...")
    print(f"📁 PDFs will be saved to: {PDF_DIR}")
    print(f"📄 Text files will be saved to: {TEXT_DIR}")
    
    chapter_urls = get_chapter_urls()
    all_texts = {}
    
    print(f"📚 Found {len(chapter_urls)} chapters/appendices to process")
    
    for name, url in tqdm(chapter_urls.items(), desc="Processing Chapters"):
        try:
            text_content = download_and_extract_text(name, url)
            if text_content:
                all_texts[name] = text_content
        except Exception as e:
            print(f"❌ Unexpected error processing {name}: {e}")
    
    print(f"✅ Completed! Successfully processed {len(all_texts)} out of {len(chapter_urls)} items")
    return all_texts


def get_available_chapters():
    """
    Get list of chapters that have already been downloaded and processed.
    
    Returns:
        list: List of chapter names that have text files available
    """
    if not TEXT_DIR.exists():
        return []
    
    available = []
    for text_file in TEXT_DIR.glob("*.txt"):
        chapter_name = text_file.stem
        available.append(chapter_name)
    
    return sorted(available)


def load_chapter_text(chapter_name):
    """
    Load text content for a specific chapter.
    
    Args:
        chapter_name: Name of the chapter (e.g., "chapter_2", "appendix_A")
        
    Returns:
        str: Text content of the chapter, or None if not found
    """
    text_path = TEXT_DIR / f"{chapter_name}.txt"
    
    if not text_path.exists():
        print(f"❌ Text file not found for {chapter_name}")
        return None
    
    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading {chapter_name}: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    print("SLP3 Content Fetcher")
    print("===================")
    
    # Check what's already available
    available = get_available_chapters()
    if available:
        print(f"📚 Already available: {', '.join(available)}")
    else:
        print("📭 No content downloaded yet")
    
    # Uncomment the line below to start fetching all content
    # all_texts = fetch_all_slp3_content()
    
    print("\nTo start downloading, uncomment the last line in this script or call:")
    print("  from src.fetch_data.fetch_jurafsky_slp3 import fetch_all_slp3_content")
    print("  all_texts = fetch_all_slp3_content()")