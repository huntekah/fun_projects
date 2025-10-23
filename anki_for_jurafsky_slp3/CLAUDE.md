# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This project automatically generates Anki flashcards from multiple educational sources using Google's Vertex AI Gemini models:

1. **SLP3 Textbook**: "Speech and Language Processing" (3rd edition) by Jurafsky and Martin - transforms academic NLP content into atomic knowledge cards
2. **LeetCode Problems**: NeetCode 150 algorithmic challenges - creates active recall cards with multiple solution approaches

Both pipelines share the same LLM infrastructure with intelligent caching and type-safe Pydantic schemas.

## Development Commands

**SLP3 Pipeline**:
- `uv run main.py --fetch --source slp3` - Download all SLP3 chapters and appendices
- `uv run main.py --create-cards` - Interactive chapter selection for card generation
- `uv run main.py --make-deck --source slp3 --chapter 8` - Create Anki deck for specific chapter

**LeetCode Pipeline**:
- `uv run main.py --fetch --source neetcode` - Download NeetCode 150 problems
- `uv run main.py --process-leetcode --source neetcode` - Generate solution cards using LLM
- `uv run main.py --make-deck --source neetcode` - Create final Anki deck
- `python neetcode_pipeline.py` - Run full NeetCode pipeline directly

**Development**:
- `uv sync` - Install dependencies
- `uv add <package>` - Add new dependency
- `make lint` - Run ruff check and format
- `make check` - Run ruff check only

**Testing** (legacy scripts scheduled for removal):
- `python test_script.py` - Test SLP3 text processing pipeline
- `python test_script2.py` - Test SLP3 atomic extraction
- `python mock_leetcode_pipeline.py` - Test LeetCode processing with sample problems

**Environment Variables**:
- `LLM_MODEL` (defaults to "gemini-2.5-flash")
- `LEETCODE_SESSION_ID` and `LEETCODE_CSRF_TOKEN` (required for LeetCode API)

## Architecture Overview

### Dual Pipeline System

**SLP3 Pipeline**: PDF → Text → 4-stage processing → Educational cards
1. **Chunking** (`src/processing/splitter.py`) - Overlapping chunks (6000 chars, 3000 overlap)
2. **LLM Cleaning** (`src/processing/preprocessor.py`) - Remove PDF artifacts, standardize formatting
3. **Intelligent Merging** (`src/processing/merger.py`) - Sequence matching handles LLM non-determinism
4. **Semantic Chunking** (`src/processing/semantic_chunker.py`) - Parse markdown into logical sections
5. **Atomic Extraction** (`src/processing/atomic_chunker.py`) - Generate Q&A, Cloze, Enumeration cards

**LeetCode Pipeline**: API → Problems → LLM analysis → Solution cards
1. **Data Fetching** (`src/fetch_data/fetch_leetcode.py`) - GraphQL API with authentication and rate limiting
2. **Card Generation** (`src/processing/leetcode_card_creation.py`) - Expert programmer LLM prompts
3. **Solution Analysis** - Multiple approaches per problem (brute force → optimized)
4. **Anki Formatting** (`src/models/leetcode_cards.py`) - Professional templates with syntax highlighting

### LLM Integration Architecture

**Core Client** (`connectors/llm/structured_gemini.py`):
- Google Vertex AI Gemini 2.5 Flash integration
- Structured output with Pydantic schemas for type safety
- Retry logic with exponential backoff (10 attempts)
- Model selection via `LLM_MODEL` environment variable

**Intelligent Caching** (`src/utils/cache.py`):
- Persistent disk cache (1GB limit) for LLM responses
- Cache keys based on model + input + schema combination
- Automatic Pydantic model serialization/deserialization
- Significant cost optimization for development iterations

### Card Type System

**SLP3 Cards** (`src/models/cards.py`) - Academic knowledge retention:
- **QACard**: Conceptual understanding ("what," "why," "how")
- **ClozeCard**: Fill-in-the-blank with `{{c1::text}}` syntax
- **EnumerationCard**: Ordered/unordered lists with context

**LeetCode Cards** (`src/models/leetcode_cards.py`) - Problem-solving skills:
- **Front**: Problem description + solution type hint
- **Back**: Key insight, strategy, implementation, complexity analysis
- **Multiple Solutions**: Separate cards for different algorithmic approaches

**Shared Infrastructure**:
- Pydantic schemas ensure type safety across both pipelines
- `genanki` creates professional Anki decks with custom CSS
- Sophisticated prompt engineering filters for educational value

## Critical Implementation Details

### Text Processing Challenges (SLP3)
- **PDF Artifacts**: Academic PDFs require multi-stage LLM cleaning for complex formatting
- **LLM Non-determinism**: Sequence matching merger handles variations between LLM runs
- **Overlap Management**: 6000/3000 char windows prevent information loss during chunking
- **Markdown Parsing**: Regex-based parsing with literal `\n` handling for LLM-cleaned text

### LeetCode API Integration
- **Authentication**: Session-based with CSRF tokens from browser cookies
- **Rate Limiting**: Built-in 2-second delays between GraphQL requests
- **Problem Filtering**: NeetCode 150 uses list ID "plakya4j" for curated problem set
- **Solution Diversity**: LLM generates multiple approaches (brute force, optimized, etc.)

### LLM Cost Optimization
- **Intelligent Caching**: Prevents redundant API calls during development iterations
- **Cache Keys**: Model + input + schema combination ensures cache validity
- **TypeAdapter**: Handles complex Pydantic union types for deserialization

## Data Organization

**Package Manager**: `uv` (Python >=3.12)
**Cache Location**: `.llm_cache/` (2GB limit, excluded from git)

**SLP3 Data Structure**:
- `data/slp3/pdf/` - Downloaded PDFs (chapters 2-28, appendices A-K)
- `data/slp3/txt/` - Extracted text
- `data/slp3/cards/` - Generated flashcards by chapter
- `data/slp3/anki_decks/` - Final .apkg files

**LeetCode Data Structure**:
- `data/neetcode/neetcode_problems.json` - Raw API data
- `data/neetcode/neetcode_150_llm_solutions.json` - LLM-generated cards
- `data/neetcode/neetcode_150_anki_cards.json` - Anki-ready format
- `data/neetcode/neetcode_150.apkg` - Final deck

## Development Notes

### Key Technical Considerations

**Prompt Engineering**: Both pipelines use extensive examples and strict schema requirements. SLP3 prompts filter out trivial historical facts and emphasize practical knowledge. LeetCode prompts focus on "aha!" moments and multiple solution approaches.

**Error Handling**: Individual failures don't stop batch processing. The system gracefully degrades and provides comprehensive logging for debugging.

**Type Safety**: Pydantic schemas throughout both pipelines ensure data integrity and provide clear contracts between processing stages. Union types use discriminated unions for reliable deserialization.

**Extension Points**: The modular design makes it easy to add new content sources. Each new source needs: fetcher, data models, processing logic, deck generation, and CLI integration.

### Pipeline-Specific Notes

**SLP3**: The caching system is critical for development cost optimization. Sequence matching handles the non-deterministic nature of LLM responses during chunk merging.

**LeetCode**: Authentication tokens must be manually extracted from browser sessions. The system processes the complete NeetCode 150 set (hardcoded problem IDs) and generates separate cards for each solution approach.