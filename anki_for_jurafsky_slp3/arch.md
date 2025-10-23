# Architecture Analysis: Anki Flashcard Generator for Educational Content

## Project Overview

This project automatically generates Anki flashcards from multiple educational sources. It supports two main content types:

1. **SLP3 Textbook**: "Speech and Language Processing" (3rd edition) by Jurafsky and Martin
2. **LeetCode Problems**: Algorithmic programming challenges from LeetCode and curated lists like NeetCode 150

The system employs sophisticated multi-stage pipelines that transform raw content into structured, educational flashcards using Google's Vertex AI Gemini models.

## High-Level Architecture

### SLP3 Pipeline
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF Files     │───▶│  Text Extraction │───▶│   4-Stage       │───▶│  Anki Deck      │
│   (SLP3 Chaps)  │    │   (PyMuPDF)      │    │   Pipeline      │    │  Generation     │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
```

### LeetCode Pipeline
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  LeetCode API   │───▶│   Problem Data   │───▶│  LLM Solution   │───▶│  Anki Deck      │
│  (NeetCode 150) │    │   Fetching       │    │   Analysis      │    │  Generation     │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
```

## Project Structure

```
anki_for_jurafsky_slp3/
├── main.py                      # Main CLI entry point
├── slp3_pipeline.py             # SLP3 pipeline orchestration
├── neetcode_pipeline.py         # NeetCode 150 pipeline orchestration
├── mock_leetcode_pipeline.py    # LeetCode testing pipeline
├── test_script.py               # SLP3 full pipeline testing
├── test_script2.py              # SLP3 atomic extraction testing
├── connectors/
│   └── llm/
│       └── structured_gemini.py # LLM client with caching
├── src/
│   ├── anki/
│   │   ├── slp3_deck_creation.py    # SLP3 Anki deck creation
│   │   └── leetcode_deck_creation.py # LeetCode Anki deck creation
│   ├── fetch_data/
│   │   ├── fetch_jurafsky_slp3.py   # PDF downloading/extraction
│   │   └── fetch_leetcode.py        # LeetCode API integration
│   ├── models/
│   │   ├── cards.py                 # SLP3 Pydantic card schemas
│   │   └── leetcode_cards.py        # LeetCode Pydantic card schemas
│   ├── processing/
│   │   ├── splitter.py              # Text chunking (SLP3)
│   │   ├── preprocessor.py          # LLM-based cleaning (SLP3)
│   │   ├── merger.py                # Intelligent chunk merging (SLP3)
│   │   ├── semantic_chunker.py      # Markdown section parsing (SLP3)
│   │   ├── atomic_chunker.py        # SLP3 flashcard extraction
│   │   └── leetcode_card_creation.py # LeetCode flashcard extraction
│   └── utils/
│       └── cache.py                 # Persistent LLM caching
└── data/
    ├── slp3/
    │   ├── pdf/                 # Downloaded PDFs
    │   ├── txt/                 # Extracted text
    │   ├── cards/               # Generated flashcards (JSON)
    │   └── anki_decks/          # Final .apkg files
    └── neetcode/
        ├── neetcode_problems.json       # Fetched problem data
        ├── neetcode_150_llm_solutions.json # LLM-generated solutions
        ├── neetcode_150_anki_cards.json    # Anki-ready cards
        └── neetcode_150.apkg            # Final Anki deck
```

## Entry Points and Execution Flow

### Main Entry Point: `main.py`

**Primary Functions:**
- `main()` - CLI argument parsing and command routing _(main.py:265)_
- `run_fetch_command()` - Downloads SLP3 PDFs _(main.py:9)_
- `run_create_cards_command()` - Interactive chapter selection for processing _(main.py:111)_
- `run_make_deck_command()` - Creates Anki decks from cards _(main.py:97)_

**How to Run:**

**SLP3 Pipeline:**
```bash
# Download SLP3 content
uv run main.py --fetch --source slp3

# Interactive card creation
uv run main.py --create-cards

# Create Anki deck for specific chapter
uv run main.py --make-deck --source slp3 --chapter 8
```

**LeetCode/NeetCode Pipeline:**
```bash
# Download NeetCode 150 problems
uv run main.py --fetch --source neetcode

# Process problems with LLM (generate solutions)
uv run main.py --process-leetcode --source neetcode

# Create Anki deck from processed cards
uv run main.py --make-deck --source neetcode
```

**Alternative Direct Execution:**
```bash
# Run full NeetCode pipeline directly
python neetcode_pipeline.py

# Test with specific problems
python mock_leetcode_pipeline.py
```

### Pipeline Orchestration: `slp3_pipeline.py`

**Core Functions:**
- `chapter_pipeline()` - Main 5-step processing pipeline _(slp3_pipeline.py:17)_
- `create_cards_for_chapters()` - Batch processing for multiple chapters _(slp3_pipeline.py:83)_

**Pipeline Stages:**
1. Split into overlapping chunks (6000 chars, 3000 overlap)
2. Clean chunks with LLM
3. Merge cleaned chunks using sequence matching
4. Split into semantic sections via markdown parsing
5. Extract atomic flashcards from each section

### LeetCode Pipeline Orchestration: `neetcode_pipeline.py`

**Core Functions:**
- `main()` - Full NeetCode 150 processing pipeline _(neetcode_pipeline.py:77)_
- `filter_problems_by_ids()` - Filters for specific problem sets _(neetcode_pipeline.py:32)_
- `save_cards_to_json()` - Persists LLM-generated cards _(neetcode_pipeline.py:51)_
- `save_anki_cards_to_json()` - Saves Anki-ready card format _(neetcode_pipeline.py:64)_

**Pipeline Stages:**
1. Load problems from JSON file
2. Filter for NeetCode 150 problem set (hardcoded list of 150 IDs)
3. Generate solution cards using LLM analysis
4. Convert to Anki-ready format with metadata
5. Save intermediate and final results

**Mock Pipeline:** `mock_leetcode_pipeline.py` _(mock_leetcode_pipeline.py:43)_
- Tests with specific problems (IDs 329, 10)
- Useful for development and debugging

### Test Scripts

> **Note:** These test scripts are scheduled for removal in favor of proper unit testing framework.

**SLP3 Testing:**
- **`test_script.py`** - Tests complete pipeline on Chapter 8 _(test_script.py:23)_
- **`test_script2.py`** - Tests atomic card extraction on specific chunks _(test_script2.py:24)_

**LeetCode Testing:**
- **`mock_leetcode_pipeline.py`** - Tests LeetCode processing with sample problems

## Data Processing Pipeline Components

### 1. Text Splitter (`src/processing/splitter.py`)

**Function:** `split_to_chunks()` _(splitter.py:4)_
- **Purpose:** Divides large text into overlapping windows
- **Default Config:** 6000 char window, 3000 char overlap
- **Logic:** Ensures last chunk is not shorter than overlap size
- **Edge Case Handling:** `_shift_start_backward()` prevents tiny final chunks

### 2. LLM Preprocessor (`src/processing/preprocessor.py`)

**Function:** `clean_chapter_text()` _(preprocessor.py:33)_
- **Purpose:** Uses Gemini to clean PDF artifacts and standardize formatting
- **Prompt Strategy:** `create_text_cleaning_prompt()` _(preprocessor.py:4)_
- **Tasks:** Remove headers/footers, join split sentences, add markdown headers
- **Special Handling:** Escapes literal `#` characters to prevent markdown conflicts

### 3. Intelligent Merger (`src/processing/merger.py`)

**Core Function:** `merge_overlapping_chunks()` _(merger.py:6)_
- **Challenge:** LLM non-determinism causes chunk variations
- **Solution:** Uses `SequenceMatcher` to find best alignment points
- **Fallback:** LLM-assisted merging when automatic matching fails _(merger.py:24)_
- **Threshold:** Minimum 20-character match required for automatic merge

### 4. Semantic Chunker (`src/processing/semantic_chunker.py`)

**Function:** `split_markdown_into_sections()` _(semantic_chunker.py:13)_
- **Purpose:** Parses cleaned markdown into logical sections
- **Pattern:** Regex-based header detection (`^#+\s+.*$`)
- **Output:** Structured sections with level, heading, content
- **Utility:** `sanitize_filename()` for safe file naming _(semantic_chunker.py:5)_

### 5. Atomic Card Extractor (`src/processing/atomic_chunker.py`)

**Main Function:** `extract_atomic_cards()` _(atomic_chunker.py:6)_
- **Input:** Semantic text section
- **Output:** List of typed flashcards (QA, Cloze, Enumeration)
- **Prompt Engineering:** Sophisticated educational principles and filtering rules
- **Quality Control:** `fix_card()` function for post-processing refinement _(atomic_chunker.py:119)_

## LeetCode Data Processing Pipeline Components

### 1. LeetCode Data Fetcher (`src/fetch_data/fetch_leetcode.py`)

**Core Class:** `LeetcodeData` _(fetch_leetcode.py:114)_
- **Purpose:** Interfaces with LeetCode's GraphQL API to fetch problem data
- **Authentication:** Requires `LEETCODE_SESSION_ID` and `LEETCODE_CSRF_TOKEN` environment variables
- **Features:** Retry logic, rate limiting, caching, pagination support

**Key Methods:**
- `all_problems_handles()` - Get all problem slugs _(fetch_leetcode.py:281)_
- `description()` - Fetch problem description _(fetch_leetcode.py:328)_
- `difficulty()` - Get difficulty level _(fetch_leetcode.py:334)_
- `tags()` - Retrieve topic tags _(fetch_leetcode.py:385)_

**NeetCode 150 Integration:**
- Supports list filtering via `list_id` parameter
- NeetCode 150 list ID: "plakya4j" _(main.py:29)_
- Automatically fetches all 150 curated problems

### 2. LeetCode Card Generator (`src/processing/leetcode_card_creation.py`)

**Main Function:** `create_leetcode_card()` _(leetcode_card_creation.py:17)_
- **Input:** Complete problem description with examples and constraints
- **Output:** `LeetcodeCard` with multiple solution approaches
- **LLM Strategy:** Expert programmer persona with educational focus

**Prompt Engineering Features:**
- **Educational Focus:** Emphasizes "aha!" moments and key insights
- **Multiple Solutions:** Generates different approaches (brute force vs. optimized)
- **Code Quality:** Minimal, clean implementations with complexity analysis
- **Mathematical Formatting:** Proper MathJax and HTML formatting

**Batch Processing:** `process_leetcode_problems()` _(leetcode_card_creation.py:136)_
- Progress tracking with tqdm
- Error handling for individual problems
- Structured output mapping problem slugs to cards

### 3. Data Validation and Loading (`src/processing/leetcode_card_creation.py`)

**Function:** `load_and_validate_problems()` _(leetcode_card_creation.py:170)_
- **Input:** JSON file with raw problem data
- **Output:** List of validated `FetchedLeetcodeProblem` objects
- **Validation:** Pydantic schema enforcement with error reporting
- **Error Handling:** Continues processing despite individual validation failures

## LLM Integration and Caching Systems

### LLM Client (`connectors/llm/structured_gemini.py`)

**Class:** `LLMClient` _(structured_gemini.py:23)_
- **Model:** Configurable via `LLM_MODEL` env var (default: "gemini-2.5-flash")
- **Features:** Structured output with Pydantic schemas
- **Retry Logic:** 10 attempts with exponential backoff _(structured_gemini.py:55)_
- **Error Handling:** Comprehensive exception handling and logging

**Key Methods:**
- `generate()` - Main generation method with caching _(structured_gemini.py:67)_
- `_generate_with_retry()` - Retry wrapper _(structured_gemini.py:61)_
- `_parse_basemodel_response()` - Type-safe response parsing _(structured_gemini.py:45)_

### Intelligent Caching (`src/utils/cache.py`)

**Core System:** `disk_cache` decorator _(cache.py:28)_
- **Storage:** DiskCache with 2GB limit (`.llm_cache/` directory)
- **Cache Key:** Combines model + input + schema hash _(cache.py:22)_
- **Serialization:** Automatic Pydantic model handling
- **Performance:** Significant cost reduction for development iterations

**Cache Features:**
- Type-aware deserialization using `TypeAdapter`
- Graceful fallback on cache corruption
- Debug logging for cache hits/misses

## Data Models and Schemas

### SLP3 Card Types (`src/models/cards.py`)

**Base Types:**
- `QACard` - Simple question/answer pairs _(cards.py:5)_
- `ClozeCard` - Fill-in-the-blank with `{{c1::text}}` syntax _(cards.py:13)_
- `EnumerationCard` - Ordered/unordered lists with context _(cards.py:22)_

**Container:**
- `AtomicCards` - Wrapper for LLM extraction results _(cards.py:39)_
- `CardType` - Union type for all card variants _(cards.py:36)_

### LeetCode Card Types (`src/models/leetcode_cards.py`)

**Data Models:**
- `FetchedLeetcodeProblem` - Raw problem data from API _(leetcode_cards.py:5)_
- `LeetCodeSolution` - Individual solution approach _(leetcode_cards.py:20)_
- `LeetcodeCard` - LLM-generated card with multiple solutions _(leetcode_cards.py:30)_
- `AnkiLeetcodeCard` - Anki-ready format with metadata _(leetcode_cards.py:36)_

**Key Features:**
- **Solution Diversity:** Multiple approaches per problem (brute force, optimized, etc.)
- **Educational Structure:** Key insights, strategies, complexity analysis, clean code
- **Metadata Integration:** Problem URLs, difficulty, tags, IDs
- **Type Safety:** Solution type hints for different algorithmic approaches

**Card Conversion:** `create_leetcode_anki_cards()` _(leetcode_cards.py:52)_
- Transforms one `LeetcodeCard` into multiple `AnkiLeetcodeCard` objects
- One Anki card per solution approach
- Preserves all problem metadata and solution details

### Schema Features (Both Types)
- Pydantic validation with descriptive field documentation
- Type-safe union handling for LLM responses
- JSON serialization support for persistence
- MathJax support for mathematical content

### SLP3 Anki Deck Creation (`src/anki/slp3_deck_creation.py`)

**Function:** `create_anki_deck()` _(slp3_deck_creation.py:74)_
- **Library:** Uses `genanki` for programmatic deck creation
- **Models:** Pre-defined templates for each card type
- **Styling:** Shared CSS for consistent appearance _(slp3_deck_creation.py:20)_
- **Features:** HTML list formatting for enumeration cards

### LeetCode Anki Deck Creation (`src/anki/leetcode_deck_creation.py`)

**Function:** `create_leetcode_anki_deck()` _(leetcode_deck_creation.py:316)_
- **Model:** Custom LeetCode card template _(leetcode_deck_creation.py:160)_
- **Advanced Styling:** Dark/light mode CSS with CSS variables _(leetcode_deck_creation.py:17)_
- **Features:** Syntax highlighting, responsive design, educational front/back structure

**Card Template Features:**
- **Front Side:** Problem description with solution type hint
- **Back Side:** Complete solution with key insight, strategy, implementation, complexity
- **Styling:** Professional appearance with syntax highlighting via highlight.js
- **Unique IDs:** GUID generation based on problem ID and solution type _(leetcode_deck_creation.py:240)_

**Data Loading:** `load_anki_cards_from_json()` _(leetcode_deck_creation.py:280)_
- Validates JSON data against `AnkiLeetcodeCard` schema
- Error handling for malformed data
- Progress reporting and statistics

## Data Storage and Organization

### SLP3 Directory Structure
- **`data/slp3/pdf/`** - Source PDF files (chapters 2-28, appendices A-K)
- **`data/slp3/txt/`** - Raw text extracted from PDFs
- **`data/slp3/cards/`** - Generated flashcards organized by chapter
- **`data/slp3/anki_decks/`** - Final Anki deck files (.apkg)

### LeetCode Directory Structure
- **`data/neetcode/neetcode_problems.json`** - Raw problem data from LeetCode API
- **`data/neetcode/neetcode_150_llm_solutions.json`** - LLM-generated `LeetcodeCard` objects
- **`data/neetcode/neetcode_150_anki_cards.json`** - Anki-ready `AnkiLeetcodeCard` objects
- **`data/neetcode/neetcode_150.apkg`** - Final Anki deck file

### File Naming Conventions

**SLP3:**
- Chapters: `chapter_8.pdf`, `chapter_8.txt`, `chapter_8.apkg`
- Appendices: `appendix_A.pdf`, `appendix_A.txt`
- Cards: `chapter_8/atomic_cards.json`

**LeetCode:**
- Raw data: `neetcode_problems.json`
- Processed cards: `neetcode_150_llm_solutions.json`
- Anki format: `neetcode_150_anki_cards.json`
- Final deck: `neetcode_150.apkg`

## Pipeline Data Flow

### SLP3 Data Flow
```
Raw PDF → Text Extraction → Chunking → LLM Cleaning → Merging → Semantic Parsing → Card Extraction → Anki Deck
   ↓           ↓              ↓           ↓            ↓           ↓               ↓              ↓
chapter_8.pdf → chapter_8.txt → chunks → cleaned_chunks → merged_text → sections → cards.json → chapter_8.apkg
```

### LeetCode Data Flow
```
LeetCode API → Problem Fetching → LLM Analysis → Solution Generation → Anki Formatting → Deck Creation
     ↓              ↓                ↓              ↓                 ↓               ↓
NeetCode 150 → neetcode_problems.json → LeetcodeCard → AnkiLeetcodeCard → neetcode_150.apkg
```

### Data Transformation Stages

**SLP3 Pipeline:**
1. **PDF → Text:** PyMuPDF extraction
2. **Text → Chunks:** Overlapping windows (6000/3000)
3. **Chunks → Clean Text:** LLM-based artifact removal
4. **Clean Chunks → Merged Text:** Sequence matching alignment
5. **Merged Text → Sections:** Markdown parsing
6. **Sections → Cards:** Educational atomic extraction
7. **Cards → Anki Deck:** genanki formatting

**LeetCode Pipeline:**
1. **API → Raw Data:** GraphQL problem fetching
2. **Raw Data → Filtered Set:** NeetCode 150 ID matching
3. **Problems → Solutions:** LLM algorithmic analysis
4. **Solutions → Anki Format:** Metadata integration
5. **Anki Cards → Deck:** Professional template rendering

## Content Fetching

### SLP3 Content Fetching (`src/fetch_data/fetch_jurafsky_slp3.py`)

**Function:** `fetch_all_slp3_content()` _(fetch_jurafsky_slp3.py:75)_
- **Source:** Stanford's official SLP3 website
- **Coverage:** Chapters 2-28 + Appendices A-K
- **Process:** Download PDF → Extract text with PyMuPDF → Save both formats
- **Caching:** Skips existing files to avoid redundant downloads

### LeetCode Content Fetching (`src/fetch_data/fetch_leetcode.py`)

**Core Integration:** Uses `python-leetcode` library for API access
- **Authentication:** Session-based with CSRF tokens
- **Rate Limiting:** Built-in delays (2 seconds between requests)
- **Retry Logic:** 3 attempts for network failures _(fetch_leetcode.py:159)_
- **GraphQL Queries:** Direct API access for complete problem data

**NeetCode 150 Fetching:** _(main.py:22)_
- **List ID:** "plakya4j" (official NeetCode 150 list)
- **Batch Processing:** Fetches all 150 problems in one operation
- **Data Completeness:** Includes description, difficulty, tags, examples, constraints
- **Output Format:** Structured JSON with `FetchedLeetcodeProblem` schema

## Configuration and Environment

### Package Management
- **Tool:** `uv` (modern Python package manager)
- **Config:** `pyproject.toml` with project dependencies
- **Key Dependencies:** google-genai, pydantic, genanki, PyMuPDF

### Environment Variables

**LLM Configuration:**
- **`LLM_MODEL`** - Gemini model selection (default: "gemini-2.5-flash")

**Authentication:**
- **Google Cloud:** Vertex AI credentials for Gemini access
- **LeetCode API:** Required for problem fetching
  - `LEETCODE_SESSION_ID` - Session cookie from browser
  - `LEETCODE_CSRF_TOKEN` - CSRF token from browser

### Development Commands
```bash
uv sync                    # Install dependencies
uv run main.py            # Run main application

# SLP3 Testing
python test_script.py     # Test SLP3 full pipeline
python test_script2.py    # Test SLP3 atomic extraction

# LeetCode Testing  
python mock_leetcode_pipeline.py  # Test LeetCode processing
python neetcode_pipeline.py       # Full NeetCode 150 pipeline
```

## Quality Assurance and Testing

### Pipeline Testing

**SLP3 Testing:**
- **Full Pipeline:** `test_script.py` processes Chapter 8 end-to-end *(scheduled for removal)*
- **Atomic Extraction:** `test_script2.py` tests specific semantic chunks *(scheduled for removal)*
- **Output Validation:** JSON serialization ensures data integrity

**LeetCode Testing:**
- **Mock Pipeline:** `mock_leetcode_pipeline.py` tests with sample problems (IDs 329, 10) *(scheduled for removal)*
- **Full Integration:** `neetcode_pipeline.py` processes complete NeetCode 150 set
- **Schema Validation:** Pydantic ensures data integrity throughout pipeline

### Error Handling
- **Graceful Degradation:** Individual section failures don't stop batch processing
- **Comprehensive Logging:** Debug information for troubleshooting
- **Retry Logic:** Robust LLM API handling with exponential backoff

## Performance Optimizations

### Caching Strategy
- **LLM Cache:** Prevents redundant API calls during development
- **File System Cache:** Persistent storage for processed content
- **Batch Processing:** Efficient handling of multiple chapters

### Cost Management
- **Intelligent Filtering:** Sophisticated prompts reduce low-value card generation
- **Chunking Strategy:** Optimal balance between context and processing efficiency
- **Model Selection:** Fast models (Gemini 2.5 Flash) for development iterations

## Educational Design Principles

### SLP3 Card Philosophy
- **Atomic Knowledge:** Each card tests one discrete concept
- **Active Recall:** Cloze deletions and targeted questions
- **Practical Focus:** Emphasizes job-interview and real-world relevance
- **Filtering:** Sophisticated LLM prompts exclude trivial historical facts

### LeetCode Card Philosophy  
- **Solution Diversity:** Multiple approaches per problem (brute force → optimized)
- **Key Insights:** Captures the "aha!" moment for each approach
- **Implementation Focus:** Clean, minimal code with complexity analysis
- **Educational Structure:** Front shows problem, back reveals solution methodology

### Card Type Comparison

| Aspect | SLP3 Cards | LeetCode Cards |
|--------|------------|----------------|
| **Primary Focus** | Conceptual understanding | Problem-solving techniques |
| **Card Types** | QA, Cloze, Enumeration | Single template with solution variants |
| **Content Source** | Academic textbook | Programming challenges |
| **Learning Goal** | Knowledge retention | Algorithm mastery |
| **Difficulty** | Variable by concept | Graded (Easy/Medium/Hard) |

## Extension Points

### Unified Architecture Benefits
- **Shared LLM Client:** Both pipelines use the same caching and retry infrastructure
- **Consistent Data Models:** Pydantic schemas ensure type safety across all pipelines
- **Modular Design:** Easy addition of new content sources (e.g., competitive programming sites)

### Additional Content Sources
- **LeetCode Integration:** Full API integration with curated problem sets
- **Extensible Framework:** Easy addition of new content sources and card types

### Card Type Extensions
- **Schema-based:** Pydantic models enable easy addition of new card formats
- **Template System:** Anki model definitions support custom card layouts

### LLM Provider Flexibility
- **Abstracted Client:** Easy swapping of LLM providers via interface consistency
- **Model Configuration:** Runtime model selection for different use cases

This architecture demonstrates a production-ready approach to educational content processing, combining robust text processing pipelines with modern LLM capabilities to create high-quality learning materials.