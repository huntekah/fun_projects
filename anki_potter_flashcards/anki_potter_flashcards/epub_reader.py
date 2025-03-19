import os
from ebooklib import epub
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path

class Chapter(BaseModel):
    title: str
    content: str

class BookContents(BaseModel):
    chapters: List[Chapter]
    # Additional fields (metadata, etc.) can be added here

DATA_DIR = Path("./data/de")


class EpubReader:
    def __init__(self):
        # Dictionary to store loaded books keyed by book_id.
        self.books: Dict[str, epub.EpubBook] = {}
    
    def load_book(self, file_path: str) -> str:
        """
        Loads an EPUB book from the given file path and stores it internally.
        Returns a book_id (in this case, the file name without extension) for reference.
        """
        book = epub.read_epub(file_path)
        book_id = os.path.splitext(os.path.basename(file_path))[0]
        self.books[book_id] = book
        return book_id
    
    def get_contents(self, book_id: str) -> BookContents:
        """
        Extracts the contents (chapters) of the loaded book identified by book_id.
        Each HTML document in the EPUB is treated as a chapter.
        Returns a BookContents object.
        """
        if book_id not in self.books:
            raise ValueError(f"Book with id '{book_id}' is not loaded.")
        
        book = self.books[book_id]
        chapters: List[Chapter] = []
        
        # Iterate over all items in the EPUB.
        for item in book.get_items():
            if isinstance(item, epub.EpubHtml):
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                header = soup.find(['h1', 'h2'])
                title = header.get_text().strip() if header else "Untitled Chapter"
                content = soup.get_text().strip()
                chapters.append(Chapter(title=title, content=content))
                
        return BookContents(chapters=chapters)

# Example usage:
if __name__ == "__main__":
    reader = EpubReader()
    
    # Example: Loading multiple books (e.g., HP1.epub, HP2.epub, ..., HP7.epub)
    for i in range(1, 8):
        file_name = DATA_DIR / f"HP{i}.epub"
        try:
            book_id = reader.load_book(file_name.absolute())
            contents = reader.get_contents(book_id)
            print(f"Book '{book_id}' has {len(contents.chapters)} chapters.")
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

