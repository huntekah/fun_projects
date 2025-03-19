from ebooklib import epub
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path
import re

class Chapter(BaseModel):
    title: str
    content: str
    number: int = 0

class BookContents(BaseModel):
    chapters: List[Chapter]
    # You can add additional metadata fields here

DATA_DIR = Path("./data/de")

class EpubReader:
    def __init__(self):
        # Store loaded books keyed by their book_id.
        self.books: Dict[str, epub.EpubBook] = {}
    
    def load_book(self, file_path: Path) -> str:
        """
        Loads an EPUB book from the given Path and stores it internally.
        Returns a book_id (here, the file name stem) for reference.
        """
        book = epub.read_epub(str(file_path))
        book_id = file_path.stem
        self.books[book_id] = book
        return book_id
    
    def get_contents(self, book_id: str) -> BookContents:
        """
        Extracts the contents (chapters) of the loaded book identified by book_id.
        Uses more robust chapter detection techniques.
        Returns a BookContents object.
        """
        if book_id not in self.books:
            raise ValueError(f"Book with id '{book_id}' is not loaded.")
        
        book = self.books[book_id]
        chapters: List[Chapter] = []
        chapter_number = 0
        
        # Get the toc (table of contents) which should list all actual chapters
        toc = book.toc
        
        # Function to recursively extract chapters from TOC
        def extract_toc_chapters(toc_items):
            result = []
            for item in toc_items:
                if isinstance(item, tuple) and len(item) >= 2:
                    # This is a TOC entry with a link
                    link = item[1]
                    if isinstance(link, str) and link.startswith('#'):
                        # Skip fragment identifiers
                        continue
                    
                    # Find the corresponding item in the book
                    for book_item in book.get_items():
                        if isinstance(book_item, epub.EpubHtml) and book_item.file_name == link:
                            title = item[0]
                            content = self._extract_content(book_item)
                            result.append((title, content))
                            break
                            
                elif isinstance(item, list):
                    # This is a nested section, recursively process it
                    result.extend(extract_toc_chapters(item))
            return result
        
        # Try to get chapters from TOC first
        toc_chapters = extract_toc_chapters(toc)
        
        # If TOC method doesn't work well, try another approach
        if not toc_chapters or len(toc_chapters) < 10:  # Assuming most HP books have more than 10 chapters
            # Get all HTML items in reading order from the spine
            spine_items = []
            for idref, linear in book.spine:
                item = book.get_item_with_id(idref)
                if item and isinstance(item, epub.EpubHtml):
                    spine_items.append(item)
            
            # Process each item to determine if it's a chapter
            for item in spine_items:
                content_str = item.get_content().decode('utf-8') if isinstance(item.get_content(), bytes) else item.get_content()
                soup = BeautifulSoup(content_str, 'html.parser')
                
                # Check if this is likely a chapter by looking for chapter indicators
                chapter_title = self._extract_chapter_title(soup)
                
                if chapter_title:
                    chapter_number += 1
                    content = soup.get_text().strip()
                    chapters.append(Chapter(
                        title=chapter_title,
                        content=content,
                        number=chapter_number
                    ))
        else:
            # Use TOC chapters
            for idx, (title, content) in enumerate(toc_chapters, 1):
                chapters.append(Chapter(
                    title=title,
                    content=content,
                    number=idx
                ))
        
        return BookContents(chapters=chapters)
    
    def _extract_content(self, item):
        """Extract text content from an EPUB item."""
        content_str = item.get_content().decode('utf-8') if isinstance(item.get_content(), bytes) else item.get_content()
        soup = BeautifulSoup(content_str, 'html.parser')
        return soup.get_text().strip()
    
    def _extract_chapter_title(self, soup):
        """
        Extract chapter title using various heuristics.
        Returns the chapter title or None if not found.
        """
        # Look for heading elements
        for heading_tag in ['h1', 'h2', 'h3']:
            heading = soup.find(heading_tag)
            if heading:
                title_text = heading.get_text().strip()
                if title_text and len(title_text) < 100:  # Reasonable title length
                    return title_text
        
        # Look for elements with specific class names that might indicate chapter titles
        for class_name in ['chapter', 'title', 'chapter-title', 'chaptertitle']:
            title_elem = soup.find(class_=re.compile(class_name, re.I))
            if title_elem:
                title_text = title_elem.get_text().strip()
                if title_text and len(title_text) < 100:
                    return title_text
        
        # Look for a pattern like "Chapter X" or "CHAPTER X" in the text
        text = soup.get_text()
        chapter_match = re.search(r'\b(?:chapter|kapitel)\s+([IVXLCDM0-9]+)', text, re.I)
        if chapter_match:
            # Find the line containing this match
            lines = text.split('\n')
            for line in lines:
                if re.search(r'\b(?:chapter|kapitel)\s+([IVXLCDM0-9]+)', line, re.I):
                    return line.strip()
        
        # If we've reached here and can't find a proper title, check if content is substantial
        # enough to be a chapter (to filter out small HTML fragments)
        text = soup.get_text().strip()
        if len(text) > 1000:  # Arbitrary threshold for a substantial chapter
            # Check if there's a strong emphasis at the beginning
            strong = soup.find(['strong', 'b'])
            if strong and strong.parent == soup.body or strong.parent.parent == soup.body:
                title_text = strong.get_text().strip()
                if title_text and len(title_text) < 100:
                    return title_text
                    
            # If all else fails but we have substantial content, use first 30 chars as title
            first_para = soup.find('p')
            if first_para:
                text = first_para.get_text().strip()
                return text[:30] + "..." if len(text) > 30 else text
                
        return None  # Not a chapter or couldn't find title

# Example usage:
if __name__ == "__main__":
    reader = EpubReader()
    
    # Process books HP1.epub, HP2.epub, ..., HP7.epub
    for i in range(1, 8):
        file_path = DATA_DIR / f"HP{i}.epub"
        try:
            book_id = reader.load_book(file_path)
            contents = reader.get_contents(book_id)
            print(f"Book '{book_id}' has {len(contents.chapters)} chapters.")
            
            # Print first few chapter titles for verification
            for idx, chapter in enumerate(contents.chapters[:5], 1):
                print(f"  Chapter {idx}: '{chapter.title}'")
            print()
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")