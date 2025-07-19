# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Anki flashcard translation project for German DTZ (Deutsch-Test für Zuwanderer) Goethe B1 vocabulary. The project loads German-English Anki decks, translates them to German-Polish using Gemini LLM, and creates new .apkg files.

## Schema Design

The project uses a **universal AnkiCard schema** with source/target field naming instead of language-specific suffixes. This prevents LLM confusion during translation:

- `full_source`, `base_source` (German content)  
- `base_target` (English → Polish translation)
- `s1_source`, `s1_target` (example sentences)
- `base_audio`, `s1_audio` (audio fields)

This design works for any language pair and makes prompts clearer for the LLM.

## LLM Output Cleaning

The project includes automatic cleaning of LLM hallucinations:

- **Problem**: LLMs sometimes output "string" or garbage in metadata fields
- **Solution**: `copy_non_translation_fields_from_original()` function 
- **Automatic**: Runs after each translation to restore original metadata
- **Preserves**: Audio fields, IDs, German content, original_order
- **Keeps**: Only the actual translations (target language fields)

This ensures clean, properly formatted output even when the LLM makes mistakes.

## Development Commands

- **Run the main script**: `uv run main.py`
- **Install dependencies**: `uv sync`
- **Add new dependencies**: `uv add <package>`
- **Update lockfile**: `uv lock`

## Project Structure

- `main.py` - Single entry point that loads an Anki deck file and displays note data using ankipandas
- `data/` - Contains the Anki deck file (`B1_Wortliste_DTZ_Goethe_vocabsentensesaudiotranslation.apkg`)
- `pyproject.toml` - Project configuration using uv package manager
- `uv.lock` - Dependency lockfile

## Key Dependencies

The project currently uses `ankipandas` for reading Anki deck files and converting them to pandas DataFrames for analysis.

## Architecture Notes

This is a simple analysis script that:
1. Loads an Anki deck file using ankipandas.Collection()
2. Accesses the notes as a pandas DataFrame via col.notes
3. Provides basic filtering and manipulation capabilities
4. Has placeholder code for writing changes back to the deck