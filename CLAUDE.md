# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of fun projects including:

1. **anki_dtz_goethe_b1_de_pl** - An Anki flashcard translator that converts German-English DTZ Goethe B1 vocabulary cards to German-Polish using LLM translation
2. **anki_potter_flashcards** - Harry Potter EPUB reader for creating Anki flashcards from German Harry Potter books
3. **ominous_timer** - A collection of timer web applications created by different LLMs as a comparison experiment
4. **ml_system_design_solutions** - Collection of ML system design solutions for real-world problems commonly asked in FAANG interviews

## Development Commands

### anki_dtz_goethe_b1_de_pl
- **Run main script**: `uv run main.py`
- **Install dependencies**: `uv sync`
- **Add dependencies**: `uv add <package>`
- **Lint check**: `make check` or `uv run ruff check .`
- **Format code**: `make format` or `uv run ruff format .`
- **Full lint + format**: `make lint`

### anki_potter_flashcards  
- **Install dependencies**: `poetry install`
- **Run EPUB reader**: `poetry run python anki_potter_flashcards/epub_reader.py`
- **Add dependencies**: `poetry add <package>`

### ominous_timer
- **View timers**: Open any `.html` file in browser (static files)

### ml_system_design_solutions
- **Browse designs**: Each system has standardized structure following `TEMPLATE.md`
- **Study examples**: Start with `nearby_places_recommender/` for complete example
- **No dependencies**: Pure documentation and Python examples (no execution environment needed)

## Architecture Overview

### anki_dtz_goethe_b1_de_pl
- **main.py**: Entry point that loads Anki decks, translates random cards using LLM, and saves new deck
- **schema.py**: Pydantic models for `AnkiCard` and `AnkiDeck` with comprehensive field definitions
- **utilities.py**: Core functions for loading/saving Anki decks using genanki
- **prompt.py**: LLM prompt generation for translation tasks
- **connectors/llm/structured_gemini.py**: Vertex AI Gemini integration with structured output
- **card_templates.py**: Anki card template definitions

Key workflow: Load original deck → Select random cards → Translate via LLM → Create new deck with translations

### anki_potter_flashcards
- **epub_reader.py**: Sophisticated EPUB parsing with multiple extraction strategies
- **Chapter extraction methods**: TOC-based, spine-based, and aggressive extraction with book-specific filtering
- **Pydantic models**: `Chapter` and `BookContents` for structured data
- **Multi-book support**: Handles HP1-HP7 with expected chapter counts and validation

The EPUB reader uses heuristics to identify chapters, handles different EPUB formats, and includes fallback extraction methods for difficult books.

### ominous_timer
Static HTML files showcasing different LLM approaches to creating timer applications. Each version demonstrates different design patterns and UI frameworks.

### ml_system_design_solutions
- **Structure**: Each system follows standardized template with requirements, design, implementation, scaling, monitoring, and alternatives
- **Focus areas**: Recommendation systems, content/media systems, data processing, classification
- **Key components**: Two-stage ML models (candidate generation + ranking), feature stores, real-time serving, A/B testing frameworks
- **Example systems**: Nearby places recommender, Instagram short videos, place deduplication, illegal content detection

The project demonstrates production ML system architecture patterns including geographic indexing, collaborative filtering, wide & deep models, and scalable inference pipelines.

## Package Management

- **anki_dtz_goethe_b1_de_pl**: Uses `uv` (modern Python package manager)
- **anki_potter_flashcards**: Uses `poetry` 
- **ominous_timer**: No dependencies (static HTML/CSS/JS)
- **ml_system_design_solutions**: No package management (documentation and examples only)

## Key Dependencies

- **anki_dtz_goethe_b1_de_pl**: genanki (Anki deck creation), google-genai (LLM integration), pydantic (data validation)
- **anki_potter_flashcards**: ebooklib (EPUB parsing), beautifulsoup4 (HTML parsing), pydantic (data models)

## Testing

Neither Python project currently has formal test suites. The projects use manual testing through their main execution scripts.