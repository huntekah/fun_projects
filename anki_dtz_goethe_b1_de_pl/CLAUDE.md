# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Anki flashcard system for German DTZ (Deutsch-Test für Zuwanderer) Goethe B1 vocabulary. The project:

1. **Loads and translates** German-English Anki decks to German-Polish using Gemini LLM
2. **Sorts cards by frequency** using German word frequency data for optimal learning order
3. **Generates bilingual TTS audio** for both German and Polish using Google Cloud TTS
4. **Creates enhanced card templates** with improved UI, audio controls, and contextual information
5. **Preserves study progress** through GUID preservation during deck transformations

## Schema Design

The project uses a **universal AnkiCard schema** with source/target field naming:

### **Core Content Fields:**
- `full_source`, `base_source` (German content)  
- `base_target` (Polish translation)
- `s1_source` through `s9_source` (German example sentences)
- `s1_target` through `s9_target` (Polish example sentences)
- `artikel_d`, `plural_d` (German grammar metadata)

### **Audio Fields:**
- `base_audio`, `s1_audio`...`s9_audio` (German audio)
- `base_target_audio`, `s1_target_audio`...`s9_target_audio` (Polish audio)

### **Metadata Fields:**
- `original_guid` (for study progress preservation)
- `original_order` (deck order metadata)

This design works for any language pair and prevents LLM confusion during translation.

## Key Features

### **1. Frequency-Based Sorting**
- Uses German frequency data from hermitdave/FrequencyWords (1.1M+ words)
- 99.9% word coverage with smart normalization (handles articles, plurals, reflexive verbs)
- Sorts cards by frequency rank (most common words first) for optimal learning

### **2. Bilingual TTS Audio Generation**
- **German TTS**: Google Cloud Studio voice (`de-DE-Studio-C`)
- **Polish TTS**: Google Cloud Standard voice (`pl-PL-Standard-G`)
- **Disk caching**: Prevents duplicate API calls and saves costs
- **Smart media filtering**: Only includes referenced audio files in .apkg

### **3. Enhanced Card Templates**
- **German → Polish**: Shows articles/plurals, context sentences, autoplay control
- **Polish → German**: Production cards with context hints
- **Audio controls**: Silence hack prevents unwanted autoplay
- **Modern styling**: Clean typography, color coding, responsive design

### **4. Study Progress Preservation**
- **GUID preservation**: Maintains Anki study history during deck updates
- **Note ID mapping**: Links translated cards to original progress
- **Safe imports**: Users can update decks without losing learning data

## Development Commands

### **Core Operations:**
- **Install dependencies**: `uv sync`
- **Run main translation**: `uv run main.py`
- **Sort by frequency**: `uv run frequency_sort.py`
- **Generate TTS audio**: `uv run generate_all_audio.py`

### **Utility Scripts:**
- **Download frequency data**: `./get_frequency_list`
- **Test TTS engine**: `uv run tts_engine.py`
- **Export to CSV**: `uv run csv_export.py`
- **Count characters**: `uv run count_characters.py`

### **Quality Assurance:**
- **Lint check**: `make check` or `uv run ruff check .`
- **Format code**: `make format` or `uv run ruff format .`
- **Full lint + format**: `make lint`

## Project Structure

### **Core Scripts:**
- `main.py` - LLM translation pipeline (German-English → German-Polish)
- `frequency_sort.py` - Sort cards by German word frequency
- `generate_all_audio.py` - Complete TTS audio generation for all fields
- `tts_engine.py` - Google Cloud TTS with caching and voice management

### **Infrastructure:**
- `schema.py` - Pydantic models for AnkiCard and AnkiDeck with audio support
- `utilities.py` - Load/save Anki decks with smart media filtering
- `card_templates.py` - Enhanced Anki card templates with bilingual audio
- `prompt.py` - LLM prompts for German-Polish translation

### **Data Processing:**
- `csv_export.py` - Export/import decks in CSV format for community editing
- `count_characters.py` - Analyze text content for TTS cost estimation
- `test_media_filtering.py` - Verify media file inclusion logic

### **Configuration:**
- `get_frequency_list` - Download German frequency data
- `pyproject.toml` - Dependencies (genanki, google-cloud-texttospeech, diskcache)
- `Makefile` - Development workflow automation

## Key Dependencies

### **Core Libraries:**
- **genanki**: Anki deck creation and .apkg generation
- **google-cloud-texttospeech**: TTS audio generation
- **diskcache**: Persistent caching for TTS API calls
- **pydantic**: Data validation and schema management

### **Language Processing:**
- **google-genai**: Gemini LLM integration for translation
- **beautifulsoup4**: HTML parsing for card templates

## Architecture Workflow

### **1. Translation Pipeline:**
```
Original Deck → LLM Translation → Translated Deck
(DE-EN)         (Gemini)         (DE-PL)
```

### **2. Frequency Sorting:**
```
Translated Deck → Frequency Data → Sorted Deck
(DE-PL)          (1.1M German)    (Optimized Order)
```

### **3. Audio Generation:**
```
Sorted Deck → TTS Engine → Complete Deck
(Text Only)   (DE+PL Audio)   (Full Media)
```

### **4. Final Output:**
- **Enhanced cards**: Beautiful templates with context and audio
- **Study-ready**: Preserves progress, optimized learning order
- **Complete media**: All audio files properly embedded

## Data Flow

### **Input:**
- `data/B1_Wortliste_DTZ_Goethe_vocabsentensesaudiotranslation.apkg` (Original DE-EN deck)

### **Intermediate:**
- `data/DTZ_Goethe_B1_DE_PL_Sample.apkg` (Translated DE-PL deck)
- `data/DTZ_Goethe_B1_DE_PL_Sample_FrequencySorted.apkg` (Frequency-sorted deck)

### **Final Output:**
- `data/DTZ_Goethe_B1_DE_PL_Complete_WithAudio.apkg` (Complete deck with audio)
- `audio_files/` (Generated TTS audio files)
- `tts_cache/` (Cached TTS responses)

## LLM Output Cleaning

The project includes automatic cleaning of LLM hallucinations:

- **Problem**: LLMs sometimes output "string" or garbage in metadata fields
- **Solution**: `copy_non_translation_fields_from_original()` function 
- **Automatic**: Runs after each translation to restore original metadata
- **Preserves**: Audio fields, IDs, German content, original_order
- **Keeps**: Only the actual translations (target language fields)

This ensures clean, properly formatted output even when the LLM makes mistakes.

## Cost Optimization

### **TTS Caching:**
- **DiskCache**: Persistent cache prevents duplicate API calls
- **Content hashing**: Same text + voice = cached result
- **Cost savings**: Significant reduction for repeated content

### **Character Counting:**
- **Full deck**: ~416k characters total (German + Polish)
- **Google TTS cost**: ~$6-10 for complete deck
- **Free tier**: 1M characters covers full deck 2.4x over

### **Smart Media Filtering:**
- **Template scanning**: Detects hardcoded media references (silence files)
- **Field analysis**: Finds all `[sound:filename.mp3]` references
- **Efficient packaging**: Only includes used media files in .apkg