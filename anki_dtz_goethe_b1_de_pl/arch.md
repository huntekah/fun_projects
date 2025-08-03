# Architecture Overview

## System Purpose

This is a comprehensive Anki flashcard system for German DTZ (Deutsch-Test für Zuwanderer) Goethe B1 vocabulary that supports both initial deck creation and ongoing collaborative maintenance. The system translates German-English vocabulary to German-Polish, optimizes learning order through frequency sorting, generates bilingual TTS audio, and provides a flexible contribution workflow.

## Core Architecture

### Data Flow Patterns

**Creation Pipeline:**
```
Original DE-EN Deck → Translation → Frequency Sorting → Audio Generation → Published Deck
```

**Contribution Pipeline:**
```
Published Deck → CSV Export → Community Editing → CSV Import → Audio Regeneration → Updated Deck
```

**Direct Editing Pipeline:**
```
Anki Desktop Edits → Deck Export → Audio Regeneration → Share
```

## Python Files Architecture

### Core Data Models

**`schema.py`** - Data Foundation
- **Purpose**: Defines the universal AnkiCard and AnkiDeck data models using Pydantic
- **Key Functions**:
  - `AnkiCard`: Comprehensive model with source/target fields, audio references, and metadata
  - `AnkiDeck`: Container model for collections of cards with deck metadata
  - Validation and serialization for all card data throughout the system

### Translation & Content Processing

**`main.py`** - Initial Translation Pipeline
- **Purpose**: Orchestrates the German-English to German-Polish translation using LLM
- **Key Functions**:
  - `main()`: Entry point that loads original deck, processes cards through LLM, saves translated deck
  - Integrates with `structured_gemini.py` for LLM translation calls
  - Applies cleaning functions to prevent LLM hallucinations in metadata fields

**`connectors/llm/structured_gemini.py`** - LLM Integration
- **Purpose**: Provides structured LLM translation using Google Gemini with caching and error handling
- **Key Functions**:
  - `StructuredGeminiClient.__init__()`: Initializes client with caching setup
  - `generate()`: Executes structured translation with schema validation and caching
  - `get_cache_stats()`: Monitors cache performance for cost optimization
  - `_create_cache_key()`: Generates consistent cache keys for content deduplication

**`prompt.py`** - LLM Prompt Engineering
- **Purpose**: Defines specialized prompts for German-Polish translation tasks
- **Key Functions**:
  - Translation prompt templates that guide the LLM to produce accurate Polish translations
  - Context-aware prompts that handle German grammar specifics (articles, plurals)
  - Structured output formatting to match the AnkiCard schema

### Content Optimization

**`frequency_sort.py`** - Learning Order Optimization
- **Purpose**: Sorts Anki cards by German word frequency for optimal learning progression
- **Key Functions**:
  - `load_frequency_list()`: Loads German frequency data from text files
  - `normalize_german_word()`: Handles German linguistic features (articles, plurals, reflexive verbs)
  - `sort_cards_by_frequency()`: Ranks cards by frequency with comprehensive statistics
  - `frequency_sort_deck()`: Complete pipeline with `--source`/`--target` file parameters
  - `main()`: CLI interface supporting flexible file paths for contribution workflow

### Audio Generation

**`generate_all_audio.py`** - TTS Audio Pipeline
- **Purpose**: Generates comprehensive bilingual TTS audio for all card fields
- **Key Functions**:
  - `generate_complete_audio_for_card()`: Creates audio for all text fields with language-specific speeds
  - `generate_audio_for_entire_deck()`: Processes entire decks with progress tracking and statistics
  - `main()`: CLI interface with `--source`/`--target` parameters for flexible workflow
  - Integrates caching and cost optimization through `tts_engine.py`

**`tts_engine.py`** - TTS Infrastructure
- **Purpose**: Provides Google Cloud TTS integration with caching and voice management
- **Key Functions**:
  - `TTSGenerator.__init__()`: Initializes TTS client with disk caching setup
  - `synthesize_speech()`: Core TTS function with language-specific voice selection and caching
  - `cache_info()`: Monitors cache performance and storage usage
  - Language-specific voice configuration (German Studio, Polish Standard)
  - Cost optimization through intelligent caching and deduplication

### Contribution Workflow

**`csv_export.py`** - Collaborative Editing Interface
- **Purpose**: Enables CSV-based collaborative editing with export/import subcommands
- **Key Functions**:
  - `export_contribution_package()`: Creates CSV + media packages for community editing
  - `load_deck_from_csv()`: Imports edited CSV data back to AnkiCard format
  - `generate_apkg_from_csv()`: Creates final APKG files from CSV with media integration
  - `main()`: CLI with subcommands (`export`/`import`) and `--source`/`--target` parameters
  - Generates contributor documentation with field editing guidelines

### Card Presentation

**`card_templates.py`** - Anki Card Design
- **Purpose**: Defines enhanced Anki card templates with bilingual audio and modern styling
- **Key Components**:
  - `DTZ_MODEL_FIELDS`: Complete field definitions for the universal schema
  - `DTZ_CARD_TEMPLATES`: Optimized card templates for German→Polish and Polish→German
  - `DTZ_CARD_CSS`: Modern styling with night mode support and audio controls
  - Silence hack implementation to prevent unwanted audio autoplay
  - Clean typography and color coding for optimal learning experience

### File Management

**`utilities.py`** - Core Infrastructure
- **Purpose**: Provides essential Anki deck loading/saving with smart media handling
- **Key Functions**:
  - `load_anki_deck()`: Loads APKG files with field mapping and validation
  - `save_anki_deck()`: Creates APKG files with optimized media filtering
  - `copy_non_translation_fields_from_original()`: Prevents LLM hallucinations in metadata
  - `get_media_files_from_cards()`: Intelligent media file detection and inclusion
  - GUID preservation for study progress continuity

### Analysis & Testing

**`count_characters.py`** - Cost Analysis
- **Purpose**: Analyzes text content for TTS cost estimation and optimization
- **Key Functions**:
  - Character counting across all German and Polish text fields
  - Cost estimation for Google Cloud TTS pricing
  - Statistics for budget planning and optimization decisions

**`test_media_filtering.py`** - Media Validation
- **Purpose**: Validates media file inclusion logic for APKG generation
- **Key Functions**:
  - Tests template scanning for hardcoded media references
  - Validates field-based media detection
  - Ensures efficient APKG packaging without unused files

### Legacy & Research Files

**`generate_deck.py`** - Alternative Generation
- **Purpose**: Alternative deck generation approach (likely legacy or experimental)
- **Functions**: Provides different deck creation strategies for comparison

**`tts_research.py`** - TTS Exploration
- **Purpose**: Research and experimentation with TTS voice options and settings
- **Functions**: Testing different voices, speeds, and quality settings

**Test Files** (`test_*.py`)
- **Purpose**: Various testing approaches for different system components
- **Functions**: Unit tests, integration tests, and validation scripts for core functionality

## Data Architecture

### Schema Design
- **Universal naming**: `source`/`target` fields work for any language pair
- **Audio integration**: Every text field has corresponding audio field
- **Metadata preservation**: Original GUIDs maintain study progress
- **Validation**: Pydantic ensures data integrity throughout pipeline

### File Flow
- **Input**: Original DE-EN APKG files
- **Processing**: Intermediate APKG files at each pipeline stage
- **Output**: Final APKG with complete audio and optimized order
- **Contribution**: CSV + media packages for collaborative editing

### Caching Strategy
- **LLM Cache**: Persistent translation caching to avoid duplicate API calls
- **TTS Cache**: Audio caching with content hashing for cost optimization
- **Media Filtering**: Smart inclusion of only referenced audio files

This architecture supports both automated pipeline processing and flexible manual workflows, enabling efficient creation and ongoing collaborative maintenance of high-quality Anki decks.