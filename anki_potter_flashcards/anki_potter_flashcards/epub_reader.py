from ebooklib import epub
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple
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
    def __init__(self, debug=False):
        # Store loaded books keyed by their book_id.
        self.books: Dict[str, epub.EpubBook] = {}
        self.debug = debug
    
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
        
        # Get expected chapter count for this book
        expected_chapters = {
            'HP1': 17,
            'HP2': 18,
            'HP3': 22,
            'HP4': 37,
            'HP5': 38,
            'HP6': 30,
            'HP7': 36
        }.get(book_id, 0)
        
        if self.debug:
            print(f"Processing {book_id} - Expected chapters: {expected_chapters}")
            
        # Try different chapter extraction methods
        chapters_from_toc = self._extract_from_toc(book)
        if len(chapters_from_toc) == expected_chapters:
            if self.debug:
                print(f"Using TOC method for {book_id} - Found exact match: {len(chapters_from_toc)} chapters")
            return BookContents(chapters=chapters_from_toc)
            
        chapters_from_spine = self._extract_from_spine(book)
        if len(chapters_from_spine) == expected_chapters:
            if self.debug:
                print(f"Using spine method for {book_id} - Found exact match: {len(chapters_from_spine)} chapters")
            return BookContents(chapters=chapters_from_spine)
            
        # If we have a reasonable number of chapters from TOC (at least 80% of expected)
        if expected_chapters > 0 and len(chapters_from_toc) >= 0.8 * expected_chapters:
            if self.debug:
                print(f"Using TOC method for {book_id} - Found {len(chapters_from_toc)} chapters (closest to expected)")
            return BookContents(chapters=chapters_from_toc)
            
        # Apply specific filtering based on book and chapter count
        if book_id == 'HP2' and len(chapters_from_toc) > 18:
            # Filter out non-chapter content for HP2
            filtered_chapters = self._filter_chapters(chapters_from_toc, book_id)
            if self.debug:
                print(f"Filtered HP2 chapters from {len(chapters_from_toc)} to {len(filtered_chapters)}")
            return BookContents(chapters=filtered_chapters)
            
        if book_id == 'HP3' and len(chapters_from_toc) > 22:
            # Filter out non-chapter content for HP3
            filtered_chapters = self._filter_chapters(chapters_from_toc, book_id)
            if self.debug:
                print(f"Filtered HP3 chapters from {len(chapters_from_toc)} to {len(filtered_chapters)}")
            return BookContents(chapters=filtered_chapters)
            
        if book_id == 'HP5' and len(chapters_from_toc) > 38:
            # Filter out non-chapter content for HP5
            filtered_chapters = self._filter_chapters(chapters_from_toc, book_id)
            if self.debug:
                print(f"Filtered HP5 chapters from {len(chapters_from_toc)} to {len(filtered_chapters)}")
            return BookContents(chapters=filtered_chapters)
            
        if book_id == 'HP7' and len(chapters_from_spine) < 36:
            # Use a more aggressive approach for HP7
            chapters = self._extract_chapters_aggressive(book)
            if self.debug:
                print(f"Using aggressive method for HP7 - Found {len(chapters)} chapters")
            return BookContents(chapters=chapters)
        
        # Use the method that found more chapters
        if len(chapters_from_toc) >= len(chapters_from_spine):
            if self.debug:
                print(f"Using TOC method for {book_id} - Found {len(chapters_from_toc)} chapters")
            return BookContents(chapters=chapters_from_toc)
        else:
            if self.debug:
                print(f"Using spine method for {book_id} - Found {len(chapters_from_spine)} chapters")
            return BookContents(chapters=chapters_from_spine)
    
    def _filter_chapters(self, chapters: List[Chapter], book_id: str) -> List[Chapter]:
        """Filter out non-chapter content based on book-specific rules."""
        filtered = []
        
        # Common patterns for chapter titles in Harry Potter books
        chapter_patterns = [
            r'^(?:chapter|kapitel)\s+\d+',  # "Chapter 1" or "Kapitel 1"
            r'^[A-Z][a-z]+\s+\d+',  # "Chapter 1" with capitalization
            r'^[A-Z\s]+$',  # All uppercase titles like "THE BOY WHO LIVED"
        ]
        
        # German Harry Potter chapter titles often start with specific words
        german_chapter_starts = [
            'Der', 'Die', 'Das', 'Ein', 'Eine', 'Im', 'Bei', 'Auf', 'Unter',
            'Durch', 'Nach', 'Vor', 'Zurück', 'Hermine', 'Harry', 'Ron',
            'Dobby', 'Eulen', 'Tante', 'Onkel', 'Hagrid', 'Zuhause', 'Hogwarts'
        ]
        
        # Only include chapters that match the patterns or start with expected words
        for chapter in chapters:
            title = chapter.title.strip()
            
            # Skip ISBN numbers, copyright info, etc.
            if re.search(r'ISBN|Copyright|Impressum', title, re.I):
                continue
                
            # Skip very short or very long titles
            if len(title) < 3 or len(title) > 100:
                continue
                
            # Check if the title matches our patterns
            pattern_match = any(re.search(pattern, title, re.I) for pattern in chapter_patterns)
            
            # Check if the title starts with common German chapter words
            german_match = any(title.startswith(word) for word in german_chapter_starts)
            
            if pattern_match or german_match:
                filtered.append(chapter)
                
        # If we've filtered too much, return the original list
        if len(filtered) < 0.7 * len(chapters):
            return chapters
            
        return filtered
    
    def _extract_from_toc(self, book: epub.EpubBook) -> List[Chapter]:
        """Extract chapters from the book's table of contents."""
        chapters = []
        chapter_number = 0
        
        def extract_toc_items(toc_items):
            nonlocal chapter_number
            result = []
            
            for item in toc_items:
                if isinstance(item, tuple) and len(item) >= 2:
                    # This is a TOC entry with a link
                    title = item[0]
                    link = item[1]
                    
                    # Skip if this is a fragment identifier
                    if isinstance(link, str) and link.startswith('#'):
                        continue
                    
                    # Find the corresponding item in the book
                    for book_item in book.get_items():
                        if isinstance(book_item, epub.EpubHtml) and book_item.file_name == link:
                            chapter_number += 1
                            content = self._extract_content(book_item)
                            result.append(Chapter(
                                title=title,
                                content=content,
                                number=chapter_number
                            ))
                            break
                            
                elif isinstance(item, list):
                    # This is a nested section, recursively process it
                    result.extend(extract_toc_items(item))
                    
            return result
        
        chapters = extract_toc_items(book.toc)
        return chapters
    
    def _extract_from_spine(self, book: epub.EpubBook) -> List[Chapter]:
        """Extract chapters from the book's spine."""
        chapters = []
        chapter_number = 0
        
        # Get all HTML items in reading order from the spine
        spine_items = []
        for idref, linear in book.spine:
            item = book.get_item_with_id(idref)
            if item and isinstance(item, epub.EpubHtml):
                spine_items.append(item)
        
        # Process each item to determine if it's a chapter
        for item in spine_items:
            try:
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
            except Exception as e:
                if self.debug:
                    print(f"Error processing spine item: {e}")
                continue
                
        return chapters
    
    def _extract_chapters_aggressive(self, book: epub.EpubBook) -> List[Chapter]:
        """More aggressive chapter extraction for difficult books."""
        chapters = []
        chapter_number = 0
        
        # Get all HTML items
        html_items = [item for item in book.get_items() if isinstance(item, epub.EpubHtml)]
        
        # Sort items by file name to try to get them in order
        html_items.sort(key=lambda x: x.file_name)
        
        # Process each item
        for item in html_items:
            try:
                content_str = item.get_content().decode('utf-8') if isinstance(item.get_content(), bytes) else item.get_content()
                soup = BeautifulSoup(content_str, 'html.parser')
                
                # Check for chapter indicators with more lenient criteria
                chapter_title = None
                
                # Try to find headings
                for heading_tag in ['h1', 'h2', 'h3', 'h4', 'strong', 'b', 'em']:
                    if heading := soup.find(heading_tag):
                        title_text = heading.get_text().strip()
                        if title_text and 3 < len(title_text) < 100:
                            chapter_title = title_text
                            break
                
                # If no heading found, look for first paragraph
                if not chapter_title:
                    if first_para := soup.find('p'):
                        text = first_para.get_text().strip()
                        if text and len(text) > 10:
                            chapter_title = text[:50] + "..." if len(text) > 50 else text
                
                # Extract content if we found a title
                if chapter_title:
                    chapter_number += 1
                    content = soup.get_text().strip()
                    # Only include if content is substantial
                    if len(content) > 1000:
                        chapters.append(Chapter(
                            title=chapter_title,
                            content=content,
                            number=chapter_number
                        ))
            except Exception as e:
                if self.debug:
                    print(f"Error in aggressive extraction: {e}")
                continue
        
        return chapters
    
    def _extract_content(self, item: epub.EpubHtml) -> str:
        """Extract text content from an EPUB item."""
        try:
            content_str = item.get_content().decode('utf-8') if isinstance(item.get_content(), bytes) else item.get_content()
            soup = BeautifulSoup(content_str, 'html.parser')
            return soup.get_text().strip()
        except Exception as e:
            if self.debug:
                print(f"Error extracting content: {e}")
            return ""
    
    def _extract_chapter_title(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract chapter title using various heuristics.
        Returns the chapter title or None if not found.
        """
        try:
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
            
            # Check for strong/emphasized text at the beginning that might be a title
            strong = soup.find(['strong', 'b'])
            if strong:
                # Safely check the parent relationship
                if strong.parent and strong.parent.name == 'body':
                    title_text = strong.get_text().strip()
                    if title_text and len(title_text) < 100:
                        return title_text
                        
            # If all else fails but we have substantial content, use first paragraph
            text = soup.get_text().strip()
            first_para = soup.find('p')
            if first_para and len(text) > 1000:
                text = first_para.get_text().strip()
                return text[:30] + "..." if len(text) > 30 else text
                    
            return None  # Not a chapter or couldn't find title
        except Exception as e:
            if self.debug:
                print(f"Error extracting chapter title: {e}")
            return None

# Example usage:
if __name__ == "__main__":
    reader = EpubReader(debug=True)
    
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