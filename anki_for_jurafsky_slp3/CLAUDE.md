# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This project automatically generates Anki flashcards from the "Speech and Language Processing" (3rd edition) textbook by Jurafsky and Martin. It uses Google's Vertex AI Gemini models to transform academic NLP content into structured spaced-repetition learning materials.

## Development Commands

**Core Commands**:
- `uv run main.py --fetch --source slp3` - Download all SLP3 chapters and appendices
- `uv run main.py` - Run main application
- `python test_script.py` - Test full text processing pipeline (chunking → cleaning → merging → semantic chunking)
- `python test_script2.py` - Test atomic flashcard extraction from semantic chunks

**Package Management**:
- `uv sync` - Install dependencies
- `uv add <package>` - Add new dependency
- Environment variable: `LLM_MODEL` (defaults to "gemini-2.5-flash")

## Architecture Overview

### Multi-Stage Text Processing Pipeline

The system implements a sophisticated 4-stage pipeline to transform raw PDF content into structured flashcards:

1. **Chunking** (`src/processing/splitter.py`) - Splits large texts into overlapping chunks (6000 chars, 3000 overlap)
2. **LLM Cleaning** (`src/processing/preprocessor.py`) - Uses Gemini to clean PDF artifacts and standardize formatting
3. **Intelligent Merging** (`src/processing/merger.py`) - Reassembles chunks using sequence matching to handle LLM-induced variations
4. **Semantic Chunking** (`src/processing/semantic_chunker.py`) - Parses markdown structure into logical sections

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

### Flashcard Generation System

**Card Types** (`src/models/cards.py`):
- **QACard**: Conceptual understanding ("what," "why," "how")
- **ClozeCard**: Fill-in-the-blank with `{{c1::text}}` syntax
- **EnumerationCard**: Ordered/unordered lists with context

**Atomic Extraction** (`src/processing/atomic_chunker.py`):
- Sophisticated prompt engineering for educational content
- Emphasizes atomic knowledge units and active recall
- Processes semantic chunks into structured flashcard objects

## Key Data Flow Patterns

1. **PDF → Text Extraction**: Uses PyMuPDF for robust text extraction from academic PDFs
2. **Chunk Processing**: Overlapping windows prevent information loss during LLM processing
3. **Overlap Resolution**: Sequence matching handles LLM non-determinism during chunk merging
4. **Semantic Parsing**: Regex-based markdown parsing with literal `\n` handling for LLM-cleaned text
5. **Knowledge Atomization**: LLM-driven extraction of discrete, testable knowledge units

## Environment and Configuration

**Package Manager**: `uv` (modern Python dependency management)
**Python Version**: >=3.12
**Cache Location**: `.llm_cache/` (excluded from git)
**Data Structure**: 
- `data/slp3/pdf/` - Downloaded PDFs
- `data/slp3/txt/` - Extracted text
- `data/slp3/semantic_chunks/` - Processed sections
- `data/slp3/atomic_results/` - Generated flashcards

## Development Notes

**LLM Cost Optimization**: The caching system is critical for development - it prevents redundant API calls when iterating on processing logic.

**Text Processing Challenges**: Academic PDFs contain complex formatting that requires multi-stage cleaning. The overlap-based chunking and sequence-matching merger handle edge cases where LLM responses vary between runs.

**Prompt Engineering**: The atomic extraction prompt uses extensive examples and strict schema requirements to ensure consistent, educational flashcard generation.

**Type Safety**: Pydantic schemas throughout the pipeline ensure data integrity and provide clear contracts between processing stages.