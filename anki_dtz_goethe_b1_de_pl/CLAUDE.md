# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Anki flashcard analysis project for German DTZ (Deutsch-Test für Zuwanderer) Goethe B1 vocabulary. The project uses the `ankipandas` library to read and analyze Anki deck files (.apkg format).

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